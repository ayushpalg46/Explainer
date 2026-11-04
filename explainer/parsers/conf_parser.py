import re
from typing import List, Dict, Optional
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation


class ConfParser(BaseParser):
    """
    Parses configuration files (.conf, .nginx, .ini, .cfg) line-by-line,
    extracting server blocks, routing locations, reverse proxy rules, ports,
    and parameters with word-by-word breakdowns, 4-year-old analogies,
    screen outcomes, and cross-file connections.
    """

    CONF_DIRECTIVES = {
        "server": ("Server Block", "Defines a virtual server context handling requests for a specific domain or port.", "Think of a server block like a dedicated ticket booth at an amusement park!"),
        "listen": ("Network Listen Port", "Configures the IP address and network port where the server accepts connections.", "Think of listen like an open doorway with an address number where visitors knock!"),
        "server_name": ("Domain Hostname", "Matches incoming HTTP request Host headers against domain names.", "Think of server_name like the name sign hanging over the door of a shop!"),
        "location": ("URL Route Handler", "Matches request URI paths to define routing, reverse proxy, or static file rules.", "Think of location like hallway signs pointing people to different rooms!"),
        "proxy_pass": ("Reverse Proxy Forwarder", "Forwards incoming requests to a backend application server.", "Think of proxy_pass like a helpful mail carrier taking a letter to the back office!"),
        "root": ("Document Root Directory", "Sets the filesystem folder where static HTML, CSS, and JS files live.", "Think of root like pointing to the exact bookshelf where your books are kept!"),
        "index": ("Default Index File", "Specifies the default file served when a directory is requested (e.g. index.html).", "Think of index like the front door mat welcoming visitors with the main menu!"),
        "include": ("File Inclusion", "Includes configuration directives from another configuration file.", "Think of include like copying pages from another guidebook into this notebook!"),
        "upstream": ("Backend Load Balancer Pool", "Defines a group of backend servers that can be referenced by proxy_pass.", "Think of upstream like a team of helper robots sharing the work equally!"),
        "try_files": ("Fallback File Lookup", "Checks for the existence of files in order and serves the first found.", "Think of try_files like checking your pocket, then your bag, then asking mom!"),
        "error_page": ("Error Handler", "Configures the custom page served for specific HTTP error status codes.", "Think of error_page like a friendly sign saying 'Oops! We are fixing this!' when something breaks."),
    }

    def __init__(self):
        super().__init__(language="Server & Infrastructure Configuration (.conf)")

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)
        lines = content.splitlines()

        analysis.beginner_story = (
            "Think of a configuration (.conf) file like a friendly traffic officer standing at a busy intersection! "
            "When people on the internet visit your website, this traffic officer looks at their ticket, "
            "tells them which room (port) to go to, delivers letters to the backend computer, and makes sure "
            "every visitor gets to the right webpage quickly and safely!"
        )

        server_blocks = 0
        locations = []
        proxies = []
        ports = []

        for idx, line in enumerate(lines, 1):
            clean = line.strip()
            if not clean or clean.startswith("#") or clean.startswith(";"):
                continue

            # 1. Block headers: server {, location /path {, upstream name {
            if clean.startswith("server {") or clean == "server":
                server_blocks += 1
                words_dict = {
                    "server": "Nginx block keyword initiating a virtual host declaration.",
                    "{": "Opening brace enclosing configuration directives for this virtual server."
                }
                analysis.elements.append(ElementExplanation(
                    name=f"Block: server (Port context)",
                    kind="server_block",
                    line_number=idx,
                    snippet=clean,
                    what_it_is="Virtual server block configuring web traffic routing.",
                    how_it_is_used=f"Starts virtual host declaration at line {idx}.",
                    where_it_is_used=f"Server context at line {idx}.",
                    why_it_works="Nginx compiles server contexts into an event-driven master-worker routing tree.",
                    best_practices_and_pitfalls="Explicitly declare server_name to prevent unintended default catch-all traffic.",
                    simple_analogy="Think of this server block like opening a new customer service booth in a big station!",
                    what_happens_on_screen="Configures how web browsers connect to this website.",
                    what_if_removed="The server stops listening for requests on this domain/port.",
                    words_breakdown=words_dict,
                    interconnection_note="Receives incoming HTTP traffic and forwards it to application files."
                ))

            # 2. Location blocks: location /api/ {
            elif clean.startswith("location "):
                m_loc = re.match(r'location\s+([^{]+)\{?', clean)
                loc_path = m_loc.group(1).strip() if m_loc else "/"
                locations.append(loc_path)

                words_dict = {
                    "location": "Nginx directive defining URL route matching rules.",
                    loc_path: f"The URL path prefix or pattern: '{loc_path}'."
                }

                analysis.elements.append(ElementExplanation(
                    name=f"Route: location {loc_path}",
                    kind="route",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"URL route handler matching requests starting with `{loc_path}`.",
                    how_it_is_used=f"Routes requests matching `{loc_path}` at line {idx}.",
                    where_it_is_used=f"Routing rule at line {idx}.",
                    why_it_works="Nginx performs prefix or regex matching on request URIs to select the winning location block.",
                    best_practices_and_pitfalls="Use exact matching (`= /`) where possible for maximum lookup performance.",
                    simple_analogy=f"Think of location '{loc_path}' like a signpost in a zoo pointing towards '{loc_path}'!",
                    what_happens_on_screen=f"Determines what users see when visiting URL `{loc_path}`.",
                    what_if_removed=f"Requests to `{loc_path}` return 404 Not Found error.",
                    words_breakdown=words_dict,
                    interconnection_note=f"Routes requests to static files or backend API endpoints."
                ))

            # 3. Directives (listen, server_name, proxy_pass, root, index, include)
            elif ";" in clean or "=" in clean:
                directive_part = clean.rstrip(";").strip()
                tokens = directive_part.split(None, 1) if "=" not in directive_part else [x.strip() for x in directive_part.split("=", 1)]
                if tokens:
                    dir_name = tokens[0].lower()
                    dir_val = tokens[1] if len(tokens) > 1 else ""

                    if dir_name in self.CONF_DIRECTIVES:
                        meta = self.CONF_DIRECTIVES[dir_name]
                        words_dict = {
                            dir_name: meta[1],
                            dir_val: f"Value parameter: `{dir_val}`."
                        }

                        if dir_name == "listen":
                            ports.append(dir_val)
                        elif dir_name == "proxy_pass":
                            proxies.append(dir_val)
                            analysis.raw_imports.append(dir_val)

                        interconn = ""
                        if dir_name == "proxy_pass":
                            interconn = f"Forwarding destination link to backend service at `{dir_val}`."
                        elif dir_name == "root":
                            interconn = f"Points to static frontend asset directory `{dir_val}`."
                        elif dir_name == "include":
                            interconn = f"Includes external configuration file `{dir_val}`."

                        analysis.elements.append(ElementExplanation(
                            name=f"{dir_name}: {dir_val[:30]}",
                            kind="directive",
                            line_number=idx,
                            snippet=clean,
                            what_it_is=f"Configuration directive `{dir_name}`: {meta[0]}.",
                            how_it_is_used=f"Configured at line {idx} with value `{dir_val}`.",
                            where_it_is_used=f"Directive at line {idx}.",
                            why_it_works="Parsed into server runtime state tables during configuration load.",
                            best_practices_and_pitfalls="Test configuration syntax using `nginx -t` before reloading.",
                            simple_analogy=meta[2],
                            what_happens_on_screen=f"Configures `{dir_name}` for incoming web visitors.",
                            what_if_removed=f"The server loses this setting and reverts to default behavior.",
                            words_breakdown=words_dict,
                            interconnection_note=interconn or "Governs web server routing and infrastructure."
                        ))
                    elif "=" in clean:
                        # INI style key = value
                        k, v = [x.strip() for x in clean.split("=", 1)]
                        analysis.elements.append(ElementExplanation(
                            name=f"Config: {k}",
                            kind="setting",
                            line_number=idx,
                            snippet=clean,
                            what_it_is=f"Configuration parameter `{k}`.",
                            how_it_is_used=f"Assigns `{k} = {v}` at line {idx}.",
                            where_it_is_used=f"Line {idx} parameter.",
                            why_it_works="Parsed into application environment dictionary.",
                            best_practices_and_pitfalls="Keep configuration comments updated when changing values.",
                            simple_analogy=f"Like setting a rule in your house: '{k}' is set to '{v}'!",
                            what_happens_on_screen="Configures application runtime setting.",
                            what_if_removed="Application falls back to internal default.",
                            words_breakdown={k: "Parameter key identifier.", v: "Assigned configuration value."}
                        ))

        detected_concepts = []
        if server_blocks:
            detected_concepts.append(f"Virtual Server Topology ({server_blocks} server block(s))")
        if ports:
            detected_concepts.append(f"Listening Ports ({', '.join(ports)})")
        if locations:
            detected_concepts.append(f"URL Route Handlers ({len(locations)} location(s))")
        if proxies:
            detected_concepts.append(f"Reverse Proxy Architecture ({len(proxies)} proxy target(s))")

        analysis.concepts_detected = detected_concepts
        analysis.frameworks_detected = ["Nginx / Reverse Proxy / Infrastructure Configuration"]
        analysis.role_in_codebase = "Web Server, Reverse Proxy & Network Routing Blueprint"
        analysis.summary = (
            f"Server configuration script containing {len(lines)} lines. "
            f"Configures {server_blocks} virtual server context(s). "
            f"{f'Listens on port(s): {', '.join(ports)}. ' if ports else ''}"
            f"{f'Defines {len(locations)} URL route(s). ' if locations else ''}"
            f"{f'Forwards traffic to {len(proxies)} backend proxy target(s). ' if proxies else ''}"
        )
        return analysis
