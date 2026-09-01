# FAR.AI build of SkyPilot

Branch `farai/v0.13.0` is upstream `v0.13.0` plus the commits listed by
`git log v0.13.0..` — each one a self-contained fix that the FAR.AI clusters need and that
is written to be upstreamable as-is. The `nrl` launcher in
[AlignmentResearch/nemo-rl](https://github.com/AlignmentResearch/nemo-rl) pins a tag of this
branch as its `skypilot` dependency, so `sky --version` on a launcher install reports the
local version label (`0.13.0+farai.1`) and a stock install does not.

## Cutting a new build

1. Commit the change on this branch (one fix per commit, subject in upstream's `[Area]` style).
2. Bump `__version__` in `sky/__init__.py` to the next `0.13.0+farai.N`.
3. Tag it: `git tag -a v0.13.0-farai.N -m 'FAR.AI build N of SkyPilot 0.13.0'` and push the
   branch and the tag.
4. Point `launcher/pyproject.toml` in nemo-rl at the new tag and relock (`uv lock` in
   `launcher/`, then at the repo root).

## Moving to a new upstream release

Create `farai/v<release>` from the upstream tag, cherry-pick the commits from the previous
branch (dropping any that upstream now carries), vendor `sky/dashboard/out` from the new PyPI
wheel, and cut build 1 as above.
