# --------------------------------------------------------------------------- write
#
# `--emit` is the only mode that touches the working tree, so the whole of the tool's restraint lives
# in these lines: plan everything first, then write. A generator that wrote three of four files and
# then refused on the fourth would leave a bundle whose parts disagree with each other, which is the
# one state this tool exists to prevent.


def _is_generated(rel: str, text: str) -> bool:
    """Whether ``text`` was produced by this tool, and so whether overwriting it destroys anything.

    JSON has no comments, so the catalog's marker is a field rather than the banner; a file that
    carries neither is somebody's work, and the difference is worth a refusal.
    """
    if GENERATED_MARK in text:
        return True
    if rel == CATALOG_REL:
        try:
            payload = json.loads(text)
        except ValueError:
            return False
        return isinstance(payload, dict) and payload.get("schema") == CATALOG_SCHEMA
    return False


def emit_bundle(root: Path, *, force: bool = False) -> tuple[int, list[str]]:
    """Render the bundle and write it, refusing to clobber anything this tool did not generate."""
    try:
        artifacts = compose_bundle(root)
    except BundleError as exc:
        return EXIT_MISSING, [f"refused: {exc}"]

    plan: list[tuple[str, Path, str]] = []
    lines: list[str] = []
    refused: list[str] = []
    for rel in sorted(artifacts):
        rendered = artifacts[rel]
        target = root / rel
        if target.is_file():
            current = target.read_text(encoding="utf-8")
            if current == rendered:
                lines.append(f"unchanged {rel}")
                continue
            if not _is_generated(rel, current) and not force:
                refused.append(rel)
                lines.append(
                    f"refused   {rel} differs and does not carry this tool's marker; it looks "
                    "hand-edited, so nothing was written anywhere - pass --force to overwrite"
                )
                continue
        plan.append((rel, target, rendered))
    if refused:
        # The refusal is printed before any write on purpose: a bundle that is half regenerated is a
        # bundle where the rules and the scrape targets disagree, and `--check` would then report
        # drift in files whose author believed they had just run `--emit`.
        return EXIT_REFUSED, lines
    for rel, target, rendered in plan:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        lines.append(f"wrote     {rel} ({len(rendered.splitlines())} lines)")
    return EXIT_OK, lines


def read_exposition(source: str) -> str:
    """The text a scrape produced, from a file or ``-`` for stdin, within the size this tool parses.

    The cap and the NUL check are not paranoia about hostile input: a truncated pipe and a binary
    dump both arrive here as "text", and both would parse into a dashboard that looks merely quiet.
    Refusing at the boundary is what keeps a quiet dashboard a statement about the service rather
    than about the shell command that fed this one.
    """
    if source == "-":
        raw = sys.stdin.buffer.read()
    else:
        path = Path(source)
        if not path.is_file():
            raise BundleError(f"--from names {source!r}, which is not a file")
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise BundleError(f"--from {source!r} could not be read: {exc}") from exc
    if len(raw) > MAX_EXPOSITION_BYTES:
        raise BundleError(
            f"exposition is {len(raw)} bytes, over the {MAX_EXPOSITION_BYTES}-byte cap; a scrape this "
            "large means a label cardinality problem, not a dashboard to render"
        )
    if b"\x00" in raw:
        raise BundleError("exposition contains a NUL byte, which no registry writes")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BundleError(f"exposition is not UTF-8: {exc}") from exc
    if not text.strip():
        raise BundleError(
            "exposition is empty; a failed curl and an idle service both look like this, and the "
            "dashboard cannot tell them apart - so neither can this tool, and it refuses"
        )
    return text


def plain_catalog(payload: dict[str, Any]) -> str:
    """The catalog as a page, for a human who has the file but not a JSON reader.

    Nothing is derived here that the payload does not already state: every line is one field printed,
    because a summary that computes its own numbers is a second document to keep honest.
    """
    lines = [
        f"schema {payload['schema']}",
        f"reader {payload['image']['reference']} "
        f"(config syntax needs >= {payload['image']['minimumVersionForHttpHeaders']})",
        f"cadence scrape={payload['cadence']['scrapeInterval']} "
        f"sustainedFor={payload['cadence']['sustainedFor']}",
        "",
        "scraped",
    ]
    for target in payload["targets"]:
        auth = f" header {target['authHeader']}" if target["authHeader"] else ""
        expansion = " (path from the environment)" if target["metricsPathIsExpansion"] else ""
        lines.append(
            f"  {target['service']:<20} {target['compose_service']}:{target['port']}"
            f"{target['metricsPath']}{auth}{expansion}"
        )
        lines.append(f"  {'':<20} port from {target['portEvidence']}; path from {target['pathEvidence']}")
        lines.append(
            f"  {'':<20} {target['familiesNamedInSource']} families named in the service's own source"
        )
    lines += ["", "not scraped"]
    for entry in payload["excluded"]:
        lines.append(f"  {entry['service']:<20} {entry['reason']}")
        lines.append(f"  {'':<20} evidence: {entry['evidence']}")
    rules = payload["rules"]
    lines += [
        "",
        f"rules: {len(rules['rendered'])} rendered of {rules['catalogSize']} in the catalog, "
        f"{len(rules['refused'])} refused",
    ]
    for rule in rules["rendered"]:
        lines.append(f"  {rule['ruleId']:<26} {rule['severity']:<9} {rule['expr']}")
        lines.append(f"  {'':<26} on {rule['family']}")
    for entry in rules["refused"]:
        lines.append(f"  {entry['ruleId']:<26} refused - {entry['reason']}")
    lines += ["", "deliberately absent"]
    for entry in payload["notIncluded"]:
        lines.append(f"  {entry['item']}")
    return "\n".join(lines) + "\n"


