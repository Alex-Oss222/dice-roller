"""Read-only, source-backed distance lookups and explicit travel estimates.

This module has no connection to the campaign store and never advances time.
"""

from copy import deepcopy
from fractions import Fraction
import json
import math
from pathlib import Path


DEFAULT_CATALOG = Path(__file__).resolve().parent.parent / "data" / "travel_distances.json"
MODES = ("road", "sea", "raven")


class TravelError(ValueError):
    """Invalid lookup, source data, or travel assumption."""


def _normalized(value, field):
    if not isinstance(value, str) or not value.strip():
        raise TravelError(f"{field} must be a nonempty string")
    return " ".join(value.split()).casefold()


def _number(value, field, *, zero_allowed=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TravelError(f"{field} must be a finite number")
    try:
        finite = math.isfinite(value)
    except (OverflowError, ValueError):
        finite = False
    if not finite or value < 0 or (value == 0 and not zero_allowed):
        boundary = "nonnegative" if zero_allowed else "positive"
        raise TravelError(f"{field} must be finite and {boundary}")
    return Fraction(str(value))


class TravelCatalog:
    """An isolated source snapshot. Public results are independent copies."""

    def __init__(self, data):
        self._data = deepcopy(data)
        try:
            if data["schema_version"] != 1:
                raise TravelError("Unsupported travel catalog schema")
            if data["units"]["distance"] != "miles" or data["units"]["rate"] != "miles per day":
                raise TravelError("Catalog must explicitly use miles and miles per day; no implicit unit conversion")
            self._base_url = data["source"]["url"].split("#", 1)[0]
            self._routes = {}
            self._names = {mode: {} for mode in MODES}
            for route in self._data["routes"]:
                mode = route["mode"]
                if mode not in MODES:
                    raise TravelError(f"Unsupported catalog mode: {mode}")
                left = _normalized(route["from"], "origin")
                right = _normalized(route["to"], "destination")
                _number(route["distance_miles"], "distance_miles")
                key = (mode, *sorted((left, right)))
                if left == right or key in self._routes:
                    raise TravelError(f"Duplicate or self route in catalog: {route['from']} / {route['to']}")
                source = route["source"]
                if not isinstance(source["cell"], str) or not isinstance(source["gid"], int):
                    raise TravelError("Each route needs a source cell and numeric sheet gid")
                self._routes[key] = route
                self._names[mode][left] = route["from"]
                self._names[mode][right] = route["to"]
            self._aliases = {_normalized(alias, "alias"): _normalized(name, "alias target")
                             for alias, name in self._data["aliases"].items()}
            self._profiles = {}
            for profile in self._data["road_profiles"]:
                profile_id = _normalized(profile["id"], "profile")
                if profile_id in self._profiles:
                    raise TravelError(f"Duplicate road profile: {profile_id}")
                for rate in profile["rates_miles_per_day"].values():
                    _number(rate, "profile rate")
                self._profiles[profile_id] = profile
        except (KeyError, TypeError, AttributeError) as exc:
            raise TravelError(f"Malformed travel catalog: {exc}") from exc

    @property
    def profiles(self):
        return deepcopy(self._data["road_profiles"])

    @property
    def summary(self):
        return {"source": deepcopy(self._data["source"]),
                "units": deepcopy(self._data["units"]),
                "route_counts": {mode: len([key for key in self._routes if key[0] == mode]) for mode in MODES},
                "aliases": deepcopy(self._data["aliases"])}

    def _place(self, mode, name):
        key = _normalized(name, "place name")
        key = self._aliases.get(key, key)
        if key not in self._names[mode]:
            raise TravelError(f"Unknown {mode} location: {name!r}; use an exact catalog name or documented alias")
        return key

    def lookup(self, mode, origin, destination):
        """Return one supplied matrix cell, never a computed shortest path."""
        mode = _normalized(mode, "mode")
        if mode not in MODES:
            raise TravelError("mode must be road, sea, or raven")
        left, right = self._place(mode, origin), self._place(mode, destination)
        route = self._routes.get((mode, *sorted((left, right))))
        if route is None:
            raise TravelError(f"No supplied {mode} route from {origin!r} to {destination!r}; no route is inferred")
        source = deepcopy(route["source"])
        source["url"] = f"{self._base_url}#gid={source['gid']}&range={source['cell']}"
        return {"mode": mode, "origin": self._names[mode][left], "destination": self._names[mode][right],
                "distance_miles": route["distance_miles"], "source": source,
                "classification": self._data["source"]["classification"],
                "units": deepcopy(self._data["units"]),
                "assumptions": deepcopy(self._data["assumptions"])}

    def estimate(self, mode, origin, destination, *, rate_mpd=None, profile=None, pace=None,
                 rest_days=0, multiplier=1, endurance_assumption=None):
        """Estimate elapsed time, without changing a campaign or claiming arrival.

        ``multiplier`` multiplies speed, not duration. Rest days are added after
        moving days. An endurance warning is advisory, never concealed.
        """
        result = self.lookup(mode, origin, destination)
        rests = _number(rest_days, "rest_days", zero_allowed=True)
        factor = _number(multiplier, "multiplier")
        if endurance_assumption is not None:
            if not isinstance(endurance_assumption, str) or not endurance_assumption.strip():
                raise TravelError("endurance_assumption must be a nonempty description of the GM's assumption")
            endurance_assumption = endurance_assumption.strip()
        rate_source = None
        if profile is not None:
            if rate_mpd is not None:
                raise TravelError("Choose rate_mpd or a road profile, not both")
            if result["mode"] != "road":
                raise TravelError("Road profiles are only available for road travel; supply rate_mpd for sea or raven")
            profile_key = _normalized(profile, "profile")
            if profile_key not in self._profiles:
                raise TravelError(f"Unknown road profile: {profile!r}")
            selected = self._profiles[profile_key]
            pace = "average" if pace is None else _normalized(pace, "pace")
            if pace not in selected["rates_miles_per_day"]:
                raise TravelError(f"Unknown pace: {pace!r}; choose {', '.join(selected['rates_miles_per_day'])}")
            rate_mpd = selected["rates_miles_per_day"][pace]
            profile = selected["id"]
            rate_source = {"profile": selected["label"], "source_range": selected["source_range"],
                           "url": self._base_url}
        else:
            if pace is not None:
                raise TravelError("pace requires an explicit road profile")
            if rate_mpd is None:
                raise TravelError("Supply rate_mpd in miles per day, or choose an explicit road profile")
        rate = _number(rate_mpd, "rate_mpd")
        # Exact fractions prevent either binary float or repeating decimal
        # rounding from adding or dropping a second at an integer boundary.
        effective_rate = rate * factor
        moving_days = Fraction(str(result["distance_miles"])) / effective_rate
        elapsed_days = moving_days + rests
        elapsed_seconds = math.ceil(elapsed_days * 86400)
        try:
            floating_values = [float(effective_rate), float(moving_days), float(elapsed_days)]
        except (OverflowError, ValueError) as exc:
            raise TravelError("Travel estimate exceeds finite numeric limits") from exc
        if not all(math.isfinite(value) and value > 0 for value in floating_values):
            raise TravelError("Travel estimate exceeds finite numeric limits")
        warnings = []
        fast_over_three_days = profile is not None and pace.startswith("fast_") and moving_days > 3
        if fast_over_three_days:
            warnings.append("ENDURANCE: This fast road pace exceeds three moving days. The source warns that fast "
                            "paces have limited endurance. This arithmetic estimate does not establish a sustainable "
                            "journey; the GM must record an endurance, relay, or staged-travel assumption before using it.")
        assumptions = result["assumptions"]
        assumptions.append(result["units"]["basis"])
        if profile is None:
            assumptions.append(f"GM-supplied travel rate: {rate_mpd} miles per day; no conversion or default rate applied.")
        else:
            assumptions.append(f"Selected road profile {profile}, pace {pace}; party suitability and route access require GM judgment.")
        assumptions.append(f"Speed multiplier {multiplier}; {rest_days} additional rest/delay days. No other delays are included.")
        if endurance_assumption is not None:
            assumptions.append(f"GM endurance assumption: {endurance_assumption}")
        result.update({"rate_mpd": rate_mpd, "effective_rate_mpd": floating_values[0],
                       "rate_source": rate_source, "profile": profile, "pace": pace,
                       "multiplier": multiplier, "moving_days": floating_values[1],
                       "rest_days": rest_days, "elapsed_days": floating_values[2],
                       "elapsed_seconds": elapsed_seconds, "warnings": warnings,
                       "requires_endurance_assumption": fast_over_three_days and endurance_assumption is None,
                       "endurance_assumption": endurance_assumption,
                       "limits": ["Fan-made route estimates, not canonical survey distances.",
                                  "Read-only arithmetic: no campaign time, task, location, delivery, or character state is changed.",
                                  "An actual turn can stop early for an encounter or decision; commit only actual elapsed time.",
                                  "Routes are symmetric for mileage only. No route-finding, access checks, unit conversions, or automatic arrivals."]})
        return result


def load_catalog(path=None):
    """Load the bundled snapshot, or a specified compatible JSON catalog."""
    try:
        data = json.loads(Path(path if path is not None else DEFAULT_CATALOG).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        raise TravelError(f"Cannot read travel catalog: {exc}") from exc
    return TravelCatalog(data)


def lookup(mode, origin, destination, *, catalog=None):
    return (catalog if catalog is not None else load_catalog()).lookup(mode, origin, destination)


def estimate(mode, origin, destination, *, rate_mpd=None, profile=None, pace=None,
             rest_days=0, multiplier=1, endurance_assumption=None, catalog=None):
    return (catalog if catalog is not None else load_catalog()).estimate(
        mode, origin, destination, rate_mpd=rate_mpd, profile=profile, pace=pace,
        rest_days=rest_days, multiplier=multiplier, endurance_assumption=endurance_assumption)
