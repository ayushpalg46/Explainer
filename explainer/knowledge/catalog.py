"""
Comprehensive Semantic Knowledge Catalog for CodeExplainer.
Contains rich pedagogical definitions, mechanics, runtime behaviors, and best practices
for HTML tags, CSS styling/animation, React/JS constructs, Python AST elements,
Rust, Java, Go, Docker directives, and Shell idioms.
"""

from typing import Dict, Any, Optional

HTML_TAG_KNOWLEDGE: Dict[str, Dict[str, str]] = {
    "html": {
        "what_it_is": "The root element of an HTML document representing the top-level container.",
        "why_it_works": "The browser parser uses <html> to initialize the DOM (Document Object Model) tree. The 'lang' attribute specifies the human language for screen readers and search engines.",
        "best_practices": "Always specify a valid 'lang' attribute (e.g. lang='en') to ensure accessibility compliance and proper hyphenation/translation."
    },
    "head": {
        "what_it_is": "The container for document metadata that is not directly rendered on the page canvas.",
        "why_it_works": "The browser reads <head> synchronously to load external stylesheets, fonts, set viewport rules, and parse meta tags before initial paint, preventing flash of unstyled content (FOUC).",
        "best_practices": "Place charset and viewport meta tags near the very top of <head> so the parser configures text encoding and mobile scaling immediately."
    },
    "body": {
        "what_it_is": "The document's primary renderable canvas containing all visual content, widgets, and layout structures.",
        "why_it_works": "Parsing the <body> builds the visible DOM elements. As elements are parsed, the browser computes CSSOM attachments to generate the render tree.",
        "best_practices": "Keep the DOM tree reasonably flat; deep nesting (>32 levels) causes significant style recalculation and layout thrashing."
    },
    "header": {
        "what_it_is": "A semantic landmark element representing introductory content or a set of navigational links.",
        "why_it_works": "Screen readers expose <header> as an ARIA 'banner' landmark (when top-level), allowing assistive technology users to jump directly to primary site navigation.",
        "best_practices": "Use <header> at the page level or within <article>/<section> to group titles, logos, and search bars. Avoid nesting <header> inside <footer>."
    },
    "nav": {
        "what_it_is": "A semantic landmark designating a section of major navigational links.",
        "why_it_works": "Assistive software maps <nav> to the 'navigation' landmark role, enabling keyboard shortcuts to skip repetitive content and reach links immediately.",
        "best_practices": "Reserve <nav> for primary navigation blocks (menus, paginations, breadcrumbs). Do not wrap all links in <nav>."
    },
    "main": {
        "what_it_is": "The dominant, unique central content area of the document body.",
        "why_it_works": "Mapped to the ARIA 'main' landmark. There should only be one non-hidden <main> per document so users can skip repeated headers and sidebars.",
        "best_practices": "Never include repeated headers, copyright notices, search banners, or global sidebars directly in <main>."
    },
    "section": {
        "what_it_is": "A generic standalone thematic grouping of content, typically with an introductory heading.",
        "why_it_works": "Creates a distinct logical region in the document outline, assisting both search engine indexers and accessibility navigation.",
        "best_practices": "Always include a descriptive heading (<h2>-<h6>) within a <section> to identify its purpose."
    },
    "article": {
        "what_it_is": "A self-contained, independently distributable or reusable composition (e.g., blog post, news story, comment).",
        "why_it_works": "Allows syndication engines (RSS, feed readers, reader mode) to extract the primary content cleanly from surrounding navigation and ads.",
        "best_practices": "An <article> should make logical sense on its own if printed or extracted from the page."
    },
    "aside": {
        "what_it_is": "A section of the page containing content tangentially related to the main content (e.g., sidebars, callouts, glossaries).",
        "why_it_works": "Maps to the 'complementary' ARIA landmark role, allowing assistive tools to skip secondary content when reading the main narrative.",
        "best_practices": "Use for related articles, author biographies, advertorial sidebars, or quick tips."
    },
    "footer": {
        "what_it_is": "A semantic container for concluding information about its nearest sectioning parent or the page.",
        "why_it_works": "Mapped to 'contentinfo' landmark role at the document root, housing legal notices, copyright, sitemaps, and contact information.",
        "best_practices": "Ensure contrast ratios for footer links comply with WCAG AA even when subdued colors are used."
    },
    "div": {
        "what_it_is": "The generic block-level flow container with no inherent semantic meaning.",
        "why_it_works": "Provides a clean hook for CSS styling (Flexbox, CSS Grid, absolute positioning) and JavaScript manipulation without imposing accessibility semantics.",
        "best_practices": "Do not use <div> for interactive buttons or links; prefer native semantic elements (<button>, <a>) to retain keyboard focus and accessibility roles."
    },
    "span": {
        "what_it_is": "A generic inline phrasing container without semantic meaning.",
        "why_it_works": "Allows styling fragments of text (colors, highlight badges, tooltips) or wrapping icons without breaking paragraph flow.",
        "best_practices": "Use only when no semantic phrasing tag (such as <em>, <strong>, <mark>, <code>) is appropriate."
    },
    "form": {
        "what_it_is": "An interactive container representing a document section containing interactive controls for submitting information.",
        "why_it_works": "Manages form submission events, keyboard submission on Enter, validation constraints, and serialization of named input fields to HTTP endpoints.",
        "best_practices": "Always pair every <input> with a valid <label> using 'for'/'id' or nested containment for full screen reader accessibility."
    },
    "input": {
        "what_it_is": "A fundamental interactive form control accepting user data input according to its 'type' attribute.",
        "why_it_works": "The browser renders specialized native controls (date picker, email keypad on mobile, file selector, checkbox, password masking) based on 'type'.",
        "best_practices": "Specify explicit 'type', 'name', 'autocomplete', and validation attributes ('required', 'pattern', 'minlength') for optimal UX."
    },
    "button": {
        "what_it_is": "An interactive push-button element activated by mouse click, keyboard (Enter/Space), or touch.",
        "why_it_works": "Has built-in accessibility tab order (tabindex=0), fires click events upon keyboard activation, and can submit/reset forms by default.",
        "best_practices": "Always set type='button' when used for UI actions outside forms, otherwise browsers default to type='submit'."
    },
    "link": {
        "what_it_is": "Specifies external resource relationships (stylesheets, preloaded fonts, favicons, canonical URLs).",
        "why_it_works": "Allows the browser engine to fetch critical external CSS and fonts. Rel='preload' instructs high-priority fetching ahead of DOM discovery.",
        "best_practices": "Use rel='preload' for critical hero fonts or LCP images, and rel='preconnect' for external asset domains."
    },
    "script": {
        "what_it_is": "Embeds executable code or references an external JavaScript file.",
        "why_it_works": "By default, scripts block DOM construction. Using 'defer' executes the script after DOM is ready without blocking, while 'async' executes as soon as downloaded.",
        "best_practices": "Always use 'defer' for client app bundles or 'type=module' which is deferred by default."
    },
    "meta": {
        "what_it_is": "Provides structured document-level metadata not expressible by other head elements.",
        "why_it_works": "Configures responsive viewport rendering (<meta name='viewport'>), character encoding (UTF-8), SEO descriptions, and OpenGraph social cards.",
        "best_practices": "Include <meta name='viewport' content='width=device-width, initial-scale=1.0'> on every responsive web page."
    },
    "canvas": {
        "what_it_is": "A bitmap canvas surface rendering procedural 2D shapes, Three.js 3D scenes, or WebGL graphics via JavaScript.",
        "why_it_works": "Provides hardware-accelerated drawing contexts (2d, webgl, webgl2, webgpu) for interactive games, data visualizations, and fluid animations.",
        "best_practices": "Provide fallback text inside <canvas> for assistive devices and account for window.devicePixelRatio to avoid blurry displays on Retina screens."
    },
    "svg": {
        "what_it_is": "Scalable Vector Graphics container defining vector paths, shapes, gradients, and icon graphics.",
        "why_it_works": "Vectors scale infinitely without pixelation or quality loss; inner paths can be styled, colored, and animated with CSS.",
        "best_practices": "Set viewBox attribute correctly and provide <title> or aria-hidden='true' for decorative icons."
    }
}

CSS_CONCEPT_KNOWLEDGE: Dict[str, Dict[str, str]] = {
    "flexbox": {
        "what_it_is": "A one-dimensional layout model providing space distribution and alignment along primary and cross axes.",
        "why_it_works": "The flex container calculates available space along the main axis ('justify-content') and cross axis ('align-items'), dynamically shrinking or expanding children based on 'flex-grow' and 'flex-shrink'.",
        "best_practices": "Ideal for navigation bars, item lists, toolbars, and centered modal boxes. Use 'gap' instead of child margins."
    },
    "css_grid": {
        "what_it_is": "A two-dimensional layout system managing both rows and columns simultaneously.",
        "why_it_works": "Creates explicit tracks using 'grid-template-columns' and 'grid-template-rows'. Elements snap into grid lines or named template areas.",
        "best_practices": "Use CSS Grid for overall page scaffolding, complex dashboards, multi-column card galleries, and asymmetrical layouts."
    },
    "media_queries": {
        "what_it_is": "Conditional CSS rules applying styles depending on device viewport dimensions, pixel density, orientation, or preferences.",
        "why_it_works": "Evaluated continuously by the browser. When the viewport crosses specified thresholds (e.g., min-width: 768px), the matching stylesheet branch overrides earlier styles.",
        "best_practices": "Follow a mobile-first design strategy using 'min-width' queries to ensure fast baseline rendering on smaller devices."
    },
    "css_variables": {
        "what_it_is": "CSS Custom Properties (e.g., --primary-color: #3b82f6) that store reusable values cascading throughout the DOM.",
        "why_it_works": "Unlike SASS variables, CSS variables are live in the browser runtime and inherit down the DOM tree, enabling instant theme switching (dark/light mode) without recompilation.",
        "best_practices": "Declare shared design tokens under the ':root' selector and override them inside '[data-theme=dark]' or '.dark' classes."
    },
    "keyframes_animation": {
        "what_it_is": "Declarative animation sequences controlling intermediate steps in a CSS animation using percentage keyframes.",
        "why_it_works": "The browser's compositor thread handles GPU-accelerated properties ('transform' and 'opacity') at 60/120fps without triggering expensive CPU layout reflows.",
        "best_practices": "Stick to animating 'transform' and 'opacity' whenever possible. Use '@media (prefers-reduced-motion: reduce)' to disable motion for sensitive users."
    },
    "tailwind_utility": {
        "what_it_is": "A utility-first CSS methodology applying atomic, pre-composed utility classes directly into markup.",
        "why_it_works": "Eliminates naming overhead and CSS bloat; modern Tailwind builds purge unused classes, yielding tiny production CSS bundles (<20KB).",
        "best_practices": "Extract repeated multi-class combinations into reusable components (e.g. React components) rather than duplicating strings."
    }
}

JS_REACT_KNOWLEDGE: Dict[str, Dict[str, str]] = {
    "useState": {
        "what_it_is": "A React Hook declaring a state variable and an updater function that triggers component re-rendering when changed.",
        "why_it_works": "React preserves state between renders by tracking hook call order within the component's internal fiber node. Updating state schedules a reconciliation pass.",
        "best_practices": "Never mutate state objects or arrays directly; always return new references (e.g. `[...items, newItem]`) to trigger accurate shallow equality checks."
    },
    "useEffect": {
        "what_it_is": "A React Hook synchronizing the component with external systems (APIs, DOM timers, WebSockets, event listeners).",
        "why_it_works": "Runs asynchronously after DOM paint. React compares values in the dependency array: if any reference has changed, the previous cleanup function is executed, followed by the new effect.",
        "best_practices": "Always declare every reactive value used inside the effect in the dependency array, and return a cleanup function to prevent memory leaks."
    },
    "useMemo": {
        "what_it_is": "A React Hook caching the result of an expensive calculation between renders.",
        "why_it_works": "React compares dependencies by reference; if unchanged, it skips re-computation and returns the previously memoized value.",
        "best_practices": "Only use for truly computationally heavy operations (e.g., sorting 10,000 records) or to preserve stable object references passed to child memo components."
    },
    "useCallback": {
        "what_it_is": "A React Hook caching a function definition between renders.",
        "why_it_works": "Prevents recreating function instances across renders, maintaining reference stability when passing callbacks to optimized children wrapped in React.memo.",
        "best_practices": "Pair with `React.memo` on the child component. Do not prematurely optimize every simple button handler."
    },
    "useRef": {
        "what_it_is": "A React Hook providing a mutable container (`.current`) that persists across renders without causing a re-render when mutated.",
        "why_it_works": "Stores direct DOM node references (e.g., for focusing an input or measuring layout) or instance variables like interval IDs.",
        "best_practices": "Do not read or write `ref.current` during rendering; only mutate it inside event handlers or `useEffect`."
    },
    "useContext": {
        "what_it_is": "A React Hook subscribing to a React Context to read shared state without manual prop drilling.",
        "why_it_works": "When the `<Context.Provider>` value changes, React automatically re-renders every component consuming that context via `useContext`.",
        "best_practices": "Split contexts by update frequency (e.g. UserAuthContext separate from ThemeContext) so components don't re-render on unrelated state changes."
    },
    "async_await": {
        "what_it_is": "Syntactic sugar built on top of JavaScript Promises for writing asynchronous code sequentially.",
        "why_it_works": "The JavaScript engine pauses execution of the async generator function while awaiting the Promise, yielding execution back to the event loop so the UI doesn't freeze.",
        "best_practices": "Always wrap await calls in `try...catch` blocks or attach `.catch()` handlers to handle network failures cleanly."
    },
    "jsx_element": {
        "what_it_is": "A declarative syntax extension for JavaScript representing UI components and DOM nodes.",
        "why_it_works": "Transpiled by Babel/SWC/esbuild into `React.createElement()` or `_jsx()` calls, creating Virtual DOM fiber objects that React diffs against the actual DOM.",
        "best_practices": "Always provide unique, stable `key` props when mapping arrays of elements to assist the reconciliation algorithm."
    }
}

PYTHON_KNOWLEDGE: Dict[str, Dict[str, str]] = {
    "decorator": {
        "what_it_is": "A metaprogramming construct (`@decorator`) that wraps and modifies or extends the behavior of a function or class.",
        "why_it_works": "Syntactic sugar for `func = decorator(func)`. It receives the original callable as an argument and returns a new wrapper callable.",
        "best_practices": "Always use `functools.wraps` inside your decorator wrapper to preserve the original function's name, docstring, and annotations."
    },
    "class": {
        "what_it_is": "An object-oriented blueprint for creating user-defined data structures containing state (attributes) and behavior (methods).",
        "why_it_works": "Instantiating a class invokes `__new__` to allocate memory followed by `__init__` to initialize instance attributes.",
        "best_practices": "Prefer composition over deep inheritance hierarchies. Use `@dataclass` or Pydantic `BaseModel` for pure data structures."
    },
    "function": {
        "what_it_is": "A modular, reusable block of code that accepts input parameters, executes statements, and returns a value.",
        "why_it_works": "Allocates a new stack frame in the Python execution environment for local variables. Supports first-class function passing and closures.",
        "best_practices": "Adhere to the Single Responsibility Principle: each function should do one thing well and be covered by unit tests."
    },
    "type_hints": {
        "what_it_is": "Type annotations specifying expected argument types and return values (e.g. `def process(x: int) -> str:`).",
        "why_it_works": "Ignored at Python runtime for performance, but statically verified by tools like `mypy` and IDEs to eliminate type errors before production.",
        "best_practices": "Annotate public APIs, functions, and complex return values to make code self-documenting and prevent runtime bugs."
    },
    "asyncio": {
        "what_it_is": "Python's standard library framework for concurrent, non-blocking asynchronous I/O using coroutines and an event loop.",
        "why_it_works": "Single-threaded cooperative multitasking: coroutines yield control (`await`) during I/O wait times, allowing thousands of connections concurrently.",
        "best_practices": "Never execute blocking CPU-heavy calculations or synchronous network calls inside an async event loop; offload them to `run_in_executor`."
    }
}

DOCKER_KNOWLEDGE: Dict[str, Dict[str, str]] = {
    "FROM": {
        "what_it_is": "Initializes a new build stage and sets the foundational base image for subsequent instructions.",
        "why_it_works": "Docker downloads the base image layers from the container registry (e.g., Docker Hub), providing the kernel filesystem and OS libraries.",
        "best_practices": "Use minimal, pinned base images (e.g. `node:20-alpine` or `python:3.12-slim`) rather than generic `latest` tags."
    },
    "WORKDIR": {
        "what_it_is": "Sets the working directory for any following `RUN`, `CMD`, `ENTRYPOINT`, `COPY`, and `ADD` instructions.",
        "why_it_works": "Creates the directory if it does not exist and ensures all relative file paths execute inside this safe container directory.",
        "best_practices": "Always set an absolute `WORKDIR` (e.g., `/app`) instead of relying on default container root directories."
    },
    "COPY": {
        "what_it_is": "Copies files or directories from the local build context into the container filesystem.",
        "why_it_works": "Each `COPY` creates an immutable image layer. Docker caches layers; if files have not changed, Docker reuses cached build layers.",
        "best_practices": "Copy package manifest files (`package.json`, `requirements.txt`) before copying source code to maximize Docker cache utilization."
    },
    "RUN": {
        "what_it_is": "Executes shell commands during container build time, committing the resulting filesystem changes into a new image layer.",
        "why_it_works": "Commonly used for installing packages, compiling code, or building production frontend assets.",
        "best_practices": "Chain related commands with `&&` and clean up package manager caches (`rm -rf /var/lib/apt/lists/*`) in the same layer to minimize image size."
    },
    "EXPOSE": {
        "what_it_is": "Documentation directive informing Docker that the container listens on the specified network ports at runtime.",
        "why_it_works": "Does not actually publish ports automatically; it serves as metadata for container runtimes and human operators.",
        "best_practices": "Always pair with `-p <host>:<container>` during `docker run` or port definitions in `docker-compose.yml`."
    },
    "ENTRYPOINT": {
        "what_it_is": "Configures a container that will run as an executable, defining the default executable process.",
        "why_it_works": "Unlike `CMD`, `ENTRYPOINT` is not easily overridden by CLI arguments; arguments passed to `docker run` are appended to the entrypoint.",
        "best_practices": "Use the exec JSON format (`ENTRYPOINT [\"python\", \"app.py\"]`) so Unix signals (SIGTERM) pass directly to the main process."
    }
}

SHELL_KNOWLEDGE: Dict[str, Dict[str, str]] = {
    "shebang": {
        "what_it_is": "The first line of an executable script starting with `#!` indicating the interpreter path.",
        "why_it_works": "The operating system kernel examines the initial bytes (magic numbers 0x23 0x21) to invoke the specified binary (e.g. `/bin/bash` or `/usr/bin/env bash`).",
        "best_practices": "Use `#!/usr/bin/env bash` for maximum portability across Unix and Linux distributions."
    },
    "pipe": {
        "what_it_is": "The pipe operator (`|`) connecting the standard output (stdout) of one command to the standard input (stdin) of another.",
        "why_it_works": "The operating system creates an in-memory unidirectional IPC buffer; both processes execute concurrently in parallel.",
        "best_practices": "Use `set -o pipefail` in your scripts so errors inside piped stages are not silently ignored."
    },
    "strict_mode": {
        "what_it_is": "Common shell safeguard flags: `set -euo pipefail`.",
        "why_it_works": "Enforces immediate script exit on command error (`-e`), treats unset variables as errors (`-u`), and fails pipelines if any stage fails (`-o pipefail`).",
        "best_practices": "Place `set -euo pipefail` at the start of every production shell script to prevent catastrophic partial script execution."
    }
}

