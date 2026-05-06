__all__ = ["main", "parse_args", "build_paths", "get_project_root", "resolve_dry_run"]


def __getattr__(name: str):
	if name in {"main", "parse_args"}:
		from carlo_bot.bootstrap.cli import main, parse_args

		exports = {"main": main, "parse_args": parse_args}
		return exports[name]

	if name in {"build_paths", "get_project_root", "resolve_dry_run"}:
		from carlo_bot.bootstrap.runtime import build_paths, get_project_root, resolve_dry_run

		exports = {
			"build_paths": build_paths,
			"get_project_root": get_project_root,
			"resolve_dry_run": resolve_dry_run,
		}
		return exports[name]

	raise AttributeError(f"module {__name__!r} has no attribute {name!r}")