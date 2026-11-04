"""
Comprehensive Semantic Knowledge Catalog for CodeExplainer.
Contains rich pedagogical definitions, 4-year-old/beginner analogies,
mechanics, what happens on screen, and what breaks if removed.
"""

from typing import Dict, Any, Optional

HTML_TAG_KNOWLEDGE: Dict[str, Dict[str, str]] = {
    "html": {
        "what_it_is": "The root element of an HTML document representing the top-level container.",
        "simple_analogy": "Think of <html> like the front and back cover of a storybook. Everything inside the book lives between these two covers!",
        "what_happens_on_screen": "It doesn't show a picture directly, but it prepares the entire white canvas for the browser to draw on.",
        "what_if_removed": "The browser gets confused about what language and standards you are using, and might display the page in broken 'quirks' mode.",
        "why_it_works": "The browser parser uses <html> to initialize the DOM tree. The 'lang' attribute specifies the human language for screen readers.",
        "best_practices": "Always specify a valid 'lang' attribute (e.g. lang='en') to ensure accessibility compliance."
    },
    "head": {
        "what_it_is": "The container for document metadata that is not directly rendered on the page canvas.",
        "simple_analogy": "Think of <head> like the brain or backpack of the webpage. You can't see the brain on the page, but it holds all the secret rules, title, and paint colors!",
        "what_happens_on_screen": "Nothing directly appears on the screen, but it sets the tab title and loads all the beautiful colors and fonts.",
        "what_if_removed": "The page loses its styling, title, and mobile screen sizing, turning into plain black text on white background.",
        "why_it_works": "The browser reads <head> synchronously to load external stylesheets, fonts, and meta tags before initial paint.",
        "best_practices": "Place charset and viewport meta tags near the very top of <head>."
    },
    "body": {
        "what_it_is": "The document's primary renderable canvas containing all visual content, widgets, and layout structures.",
        "simple_analogy": "Think of <body> like the stage in a theater! Every actor, costume, picture, and button you see performs on this stage.",
        "what_happens_on_screen": "Everything you actually see with your eyes—buttons, cards, pictures, text—lives inside here.",
        "what_if_removed": "Your webpage would be a completely blank white screen!",
        "why_it_works": "Parsing <body> builds visible DOM elements and calculates CSSOM attachments to generate the render tree.",
        "best_practices": "Keep the DOM tree reasonably flat; deep nesting (>32 levels) causes layout thrashing."
    },
    "div": {
        "what_it_is": "The generic block-level flow container used to group elements together.",
        "simple_analogy": "Think of a <div> like an invisible cardboard box! You put toys (buttons, pictures, text) into the box so you can move or color them all at once.",
        "what_happens_on_screen": "By itself it is completely invisible, but it groups its children together onto a new line.",
        "what_if_removed": "The items inside spill all over the page and lose their neat layout, positioning, and background colors.",
        "why_it_works": "Provides a clean hook for CSS styling (Flexbox, Grid) and JavaScript manipulation without imposing semantics.",
        "best_practices": "Do not use <div> for interactive buttons or links; prefer native semantic elements (<button>, <a>)."
    },
    "span": {
        "what_it_is": "A generic inline phrasing container used to style small snippets of text.",
        "simple_analogy": "Think of a <span> like a colored highlighter pen! You use it to highlight just one word or phrase inside a sentence.",
        "what_happens_on_screen": "It stays on the same line with neighboring words and applies special colors or badges without breaking the sentence.",
        "what_if_removed": "The highlighted word loses its special color or styling and looks like the rest of the sentence.",
        "why_it_works": "Allows styling fragments of text or wrapping icons without breaking paragraph flow.",
        "best_practices": "Use only when no semantic phrasing tag (such as <em>, <strong>, <mark>) is appropriate."
    },
    "h1": {
        "what_it_is": "The most important top-level heading on the webpage.",
        "simple_analogy": "Think of <h1> like the big giant title on the cover of a storybook or newspaper!",
        "what_happens_on_screen": "Displays big, bold, proud headline text that immediately tells visitors what the page is about.",
        "what_if_removed": "Visitors and search engines (like Google) won't know the main topic of your page.",
        "why_it_works": "Screen readers announce <h1> as the primary landmark; search engines use it for search indexing.",
        "best_practices": "Only use one <h1> per page for optimal accessibility and SEO."
    },
    "h2": {
        "what_it_is": "A secondary section heading.",
        "simple_analogy": "Think of <h2> like the chapter title in a book!",
        "what_happens_on_screen": "Displays bold section text that separates chapters or topics on the page.",
        "what_if_removed": "The page becomes a giant wall of text without clear chapter breaks.",
        "why_it_works": "Creates document outline levels that screen reader users can jump between using keyboard shortcuts.",
        "best_practices": "Follow numerical heading order (h1, then h2, then h3). Do not skip levels."
    },
    "p": {
        "what_it_is": "A paragraph of plain text.",
        "simple_analogy": "Think of <p> like a friendly sentence or paragraph in a letter to your friend.",
        "what_happens_on_screen": "Renders readable sentences with comfortable spacing above and below so it's easy to read.",
        "what_if_removed": "Sentences get squished together into one giant unreadable clump.",
        "why_it_works": "The browser applies standard block margins and typographic word-wrapping.",
        "best_practices": "Wrap all prose text in <p> tags rather than floating bare text inside <div>."
    },
    "button": {
        "what_it_is": "An interactive push-button element activated by mouse click, keyboard, or touch.",
        "simple_analogy": "Think of a <button> like a magical doorbell on a house! When you press it, a bell rings or a door opens!",
        "what_happens_on_screen": "Renders a clickable button that highlights when you hover over it or tap it.",
        "what_if_removed": "Users cannot submit forms, open dialogs, or trigger actions with their mouse or keyboard.",
        "why_it_works": "Has built-in accessibility tab order (tabindex=0) and triggers click events upon pressing Enter or Spacebar.",
        "best_practices": "Always set type='button' when used for UI actions outside forms to avoid unintended form submissions."
    },
    "a": {
        "what_it_is": "An anchor hyperlink connecting to another web page, file, or page section.",
        "simple_analogy": "Think of <a> like a magic teleportation door! You step through it (click it) and zoom to another room or website!",
        "what_happens_on_screen": "Shows colored, underlined text (or a button) that turns into a hand cursor when hovered.",
        "what_if_removed": "Users cannot navigate to other pages or links.",
        "why_it_works": "The browser navigates to the URL specified in the 'href' attribute when clicked.",
        "best_practices": "Provide clear descriptive text (e.g. 'View Dashboard') instead of generic words like 'Click here'."
    },
    "img": {
        "what_it_is": "An image element embedding a picture into the webpage.",
        "simple_analogy": "Think of <img> like a photo frame hung up on the wall!",
        "what_happens_on_screen": "Displays a picture, photo, illustration, or graphic.",
        "what_if_removed": "The picture vanishes and leaves an empty gap.",
        "why_it_works": "Fetches the image file from the 'src' path and renders it according to width and height dimensions.",
        "best_practices": "Always provide an 'alt' attribute describing the image for people who cannot see it."
    },
    "link": {
        "what_it_is": "Specifies external resource relationships (stylesheets, fonts, favicons).",
        "simple_analogy": "Think of <link> like a phone call to a paint shop: 'Hey, please send over the style.css paint bucket so I can paint my page!'",
        "what_happens_on_screen": "Invisible on the page itself, but it gives the entire page its vibrant colors, fonts, and layout.",
        "what_if_removed": "The webpage loses its external CSS stylesheets and turns into bare, unstyled black-and-white text.",
        "why_it_works": "The browser downloads and applies the CSS file specified in 'href' before drawing the page.",
        "best_practices": "Use rel='stylesheet' for CSS files and rel='preconnect' for external font servers."
    },
    "script": {
        "what_it_is": "Embeds executable JavaScript code or links an external script file.",
        "simple_analogy": "Think of <script> like a magic spellbook or brain chip! It gives the webpage life so it can move, think, and respond when you tap things.",
        "what_happens_on_screen": "Invisible directly, but powers animations, button clicks, API calls, and interactive games.",
        "what_if_removed": "The page becomes a frozen statue: buttons won't do anything when clicked and dynamic data won't load.",
        "why_it_works": "The browser's JavaScript engine (V8, SpiderMonkey) executes the code or fetches the file in 'src'.",
        "best_practices": "Use 'defer' or 'type=\"module\"' so the script doesn't freeze the screen while downloading."
    },
    "header": {
        "what_it_is": "A semantic landmark representing introductory content or top navigation.",
        "simple_analogy": "Think of <header> like the roof or entrance sign of a shop showing the store name and navigation arrows.",
        "what_happens_on_screen": "Displays the top bar of the website with the logo, title, and menu buttons.",
        "what_if_removed": "The page loses its top navigation structure.",
        "why_it_works": "Exposes an ARIA 'banner' landmark so screen readers can jump directly to the site menu.",
        "best_practices": "Place the main logo, title, and search bar inside the <header>."
    },
    "nav": {
        "what_it_is": "A semantic landmark designating a section of major navigational links.",
        "simple_analogy": "Think of <nav> like a signpost with arrows pointing: 'To the Playground', 'To the Cafeteria', 'To the Gift Shop'!",
        "what_happens_on_screen": "Groups navigation links into a clean menu bar.",
        "what_if_removed": "Users and screen readers have to hunt through the whole page to find the menu.",
        "why_it_works": "Assistive software maps <nav> to the 'navigation' landmark role.",
        "best_practices": "Reserve for primary navigation blocks (menus, breadcrumbs). Do not wrap every single link."
    },
    "main": {
        "what_it_is": "The dominant, unique central content area of the document body.",
        "simple_analogy": "Think of <main> like the main dish at dinner! Everything else (header, footer) is just the napkin and cutlery.",
        "what_happens_on_screen": "Contains the actual article, dashboard, or game you came to see.",
        "what_if_removed": "Screen readers cannot easily skip past repeated headers to get straight to the good stuff.",
        "why_it_works": "Mapped to the ARIA 'main' landmark. There should only be one non-hidden <main> per document.",
        "best_practices": "Never put repeated global headers or footers inside <main>."
    },
    "footer": {
        "what_it_is": "A semantic container for concluding information, copyright, and bottom links.",
        "simple_analogy": "Think of <footer> like the bottom floor of a building where you find the exit sign and copyright stamp.",
        "what_happens_on_screen": "Displays the bottom strip with copyright, privacy policy links, and social icons.",
        "what_if_removed": "Visitors won't know who made the website or where to find legal and contact info.",
        "why_it_works": "Mapped to 'contentinfo' landmark role at the document root.",
        "best_practices": "Keep footer contrast high so small copyright text remains readable."
    },
    "form": {
        "what_it_is": "An interactive container for submitting user information.",
        "simple_analogy": "Think of <form> like an envelope or postal letter where you write your name and drop it in the mailbox!",
        "what_happens_on_screen": "Groups input boxes and submit buttons together.",
        "what_if_removed": "Pressing Enter won't submit the inputs and data cannot be packaged together easily.",
        "why_it_works": "Manages form submission events, validation constraints, and serialization of named fields.",
        "best_practices": "Always pair every <input> with a valid <label>."
    },
    "input": {
        "what_it_is": "An interactive control accepting user typing, checkboxes, or file uploads.",
        "simple_analogy": "Think of <input> like a blank fill-in-the-blank line in a coloring workbook!",
        "what_happens_on_screen": "Renders an empty box where you can type your name, password, or check a box.",
        "what_if_removed": "Users cannot type answers or enter information.",
        "why_it_works": "The browser presents native inputs (text box, password dots, date picker) based on 'type'.",
        "best_practices": "Always specify explicit 'type', 'name', and 'placeholder' attributes."
    },
    "canvas": {
        "what_it_is": "A bitmap canvas surface rendering procedural 2D shapes or 3D WebGL graphics.",
        "simple_analogy": "Think of <canvas> like a blank sheet of paper and a robotic painter with paintbrushes ready to draw anything!",
        "what_happens_on_screen": "Displays smooth custom animations, 3D rotating models, or video game graphics.",
        "what_if_removed": "The 3D game or interactive chart disappears completely.",
        "why_it_works": "Provides hardware-accelerated drawing contexts (2d, webgl) powered by the computer's graphics card.",
        "best_practices": "Account for devicePixelRatio so graphics don't look blurry on high-resolution screens."
    },
    "svg": {
        "what_it_is": "Scalable Vector Graphics container defining sharp mathematical shapes and icons.",
        "simple_analogy": "Think of <svg> like drawing with rubber bands! No matter how big you stretch it, it never gets blurry or pixelated!",
        "what_happens_on_screen": "Displays razor-sharp icons, logos, and vector illustrations.",
        "what_if_removed": "The icon or logo disappears.",
        "why_it_works": "Uses mathematical formulas for lines and curves rather than pixel grids.",
        "best_practices": "Always include a 'viewBox' attribute so the SVG scales automatically."
    }
}

CSS_CONCEPT_KNOWLEDGE: Dict[str, Dict[str, str]] = {
    "flexbox": {
        "what_it_is": "A layout engine that arranges items neatly in a single line (row or column).",
        "simple_analogy": "Think of Flexbox like a teacher arranging children in a neat line holding hands, spacing them evenly across the playground!",
        "what_happens_on_screen": "Buttons, cards, or menu items sit side-by-side with perfect equal spacing and never bump into each other.",
        "what_if_removed": "Items fall on top of each other in a messy, ugly vertical pile.",
        "why_it_works": "The flex container calculates available space along the main axis ('justify-content') and cross axis ('align-items').",
        "best_practices": "Use 'gap' for spacing between items instead of adding margins to every child."
    },
    "css_grid": {
        "what_it_is": "A two-dimensional layout engine managing both rows and columns like a checkerboard.",
        "simple_analogy": "Think of CSS Grid like a giant ice-cube tray or bento box! You give each food item its own special compartment.",
        "what_happens_on_screen": "Creates neat photo grids, card galleries, and multi-column dashboards.",
        "what_if_removed": "The neat table or card grid collapses into a single disorganized list.",
        "why_it_works": "Creates explicit tracks using 'grid-template-columns' and 'grid-template-rows'.",
        "best_practices": "Use CSS Grid for overall page layout and card galleries; use Flexbox inside individual cards."
    },
    "media_queries": {
        "what_it_is": "Conditional CSS rules applying styles depending on device screen width or orientation.",
        "simple_analogy": "Think of media queries like an outfit changer! When you go outside in the cold (small mobile phone), it puts on a winter jacket, and in the sun (big monitor), it puts on sunglasses!",
        "what_happens_on_screen": "Rearranges cards into a single column on phones so text doesn't look tiny, and expands into 3 columns on desktops.",
        "what_if_removed": "The mobile website looks broken, with text overflowing or requiring awkward sideways scrolling.",
        "why_it_works": "Evaluated continuously by the browser engine against the active viewport width.",
        "best_practices": "Follow a mobile-first strategy using 'min-width' queries."
    },
    "css_variables": {
        "what_it_is": "Reusable color and size tokens (like `--primary-color: #3b82f6`).",
        "simple_analogy": "Think of a CSS variable like a bucket of blue paint with a label 'MY_FAVORITE_BLUE'. Whenever you want blue, you just point to the bucket!",
        "what_happens_on_screen": "Allows changing all buttons from light blue to dark theme with one single switch.",
        "what_if_removed": "You have to hunt down and re-type the color in 500 different places if you ever want to change it.",
        "why_it_works": "CSS variables inherit down the DOM tree and update instantly in memory without reloading the page.",
        "best_practices": "Declare theme variables inside ':root' and override them under '.dark' for easy dark mode."
    },
    "keyframes_animation": {
        "what_it_is": "A rule that makes elements move, spin, fade, or bounce over time.",
        "simple_analogy": "Think of @keyframes like a flipbook cartoon! You draw how the toy looks at the start (0%) and end (100%), and the computer flips the pages super fast!",
        "what_happens_on_screen": "Buttons pulse, loading spinners twirl, and menus glide smoothly into view.",
        "what_if_removed": "Everything stays completely still and motionless.",
        "why_it_works": "The computer GPU smoothly interpolates values between each keyframe at 60 or 120 frames per second.",
        "best_practices": "Animate 'transform' and 'opacity' to ensure buttery smooth 60fps animations without lag."
    },
    "tailwind_utility": {
        "what_it_is": "A utility-first CSS methodology applying pre-made styling classes directly to HTML tags.",
        "simple_analogy": "Think of Tailwind like pre-glued Lego stickers! Instead of mixing paint, you just stick 'p-4' (padding) and 'bg-blue' directly onto the Lego brick!",
        "what_happens_on_screen": "Styles the element immediately without writing custom separate CSS files.",
        "what_if_removed": "The markup loses its styling classes.",
        "why_it_works": "Tailwind compiles only the used utility classes into a tiny optimized stylesheet.",
        "best_practices": "Extract repeated multi-class combinations into reusable components."
    }
}

JS_REACT_KNOWLEDGE: Dict[str, Dict[str, str]] = {
    "useState": {
        "what_it_is": "A React Hook that stores memory (state) that redraws the screen when changed.",
        "simple_analogy": "Think of useState like an erasable whiteboard scoreboard! Whenever somebody scores a goal, you erase the old number, write the new number, and everyone in the stadium cheers!",
        "what_happens_on_screen": "The number on the screen (like a counter or shopping cart item count) instantly updates before your eyes.",
        "what_if_removed": "The computer forgets what the user clicked, and the numbers on the screen never change.",
        "why_it_works": "React preserves state between renders and triggers a re-render pass whenever the updater function is called.",
        "best_practices": "Never modify state directly (don't do count = count + 1); always call the updater function setCount(count + 1)."
    },
    "useEffect": {
        "what_it_is": "A React Hook that runs side effects (fetching data, setting timers, listening to events).",
        "simple_analogy": "Think of useEffect like an automatic helper who does a chore as soon as you finish building your Lego set, like turning on the Lego streetlights!",
        "what_happens_on_screen": "Automatically loads data from the internet or starts a timer right after the page appears.",
        "what_if_removed": "External data won't load from servers, and timers or window listeners won't start.",
        "why_it_works": "Runs asynchronously after the component is rendered to the DOM.",
        "best_practices": "Always declare dependencies in the dependency array `[]` and return a cleanup function."
    },
    "useMemo": {
        "what_it_is": "A React Hook caching the result of an expensive calculation between renders.",
        "simple_analogy": "Think of useMemo like writing down the answer to a hard math puzzle on a sticky note so you never have to solve it again!",
        "what_happens_on_screen": "Keeps the app silky smooth and prevents lagging during heavy calculations.",
        "what_if_removed": "The computer re-calculates the puzzle every millisecond, making the app sluggish.",
        "why_it_works": "React checks if dependencies changed; if identical, it reuses the cached value.",
        "best_practices": "Use only for heavy computational tasks."
    },
    "useCallback": {
        "what_it_is": "A React Hook caching a function definition between renders.",
        "simple_analogy": "Think of useCallback like keeping the exact same key to your toybox instead of making a brand new key every single second!",
        "what_happens_on_screen": "Prevents child components from re-rendering unnecessarily.",
        "what_if_removed": "Child components might re-render needlessly on every keystroke.",
        "why_it_works": "Preserves functional reference stability across renders.",
        "best_practices": "Pair with React.memo on child components."
    },
    "useRef": {
        "what_it_is": "A React Hook providing a mutable container (`.current`) that persists across renders without triggering a re-render.",
        "simple_analogy": "Think of useRef like a secret pocket! You can put a marble in your pocket, take it out, or check it without disturbing anyone.",
        "what_happens_on_screen": "Allows focusing an input box or measuring the size of an element on the screen.",
        "what_if_removed": "You cannot directly grab DOM elements or hold persistent timers.",
        "why_it_works": "Returns a persistent reference object `{current: ...}` tied to the component fiber.",
        "best_practices": "Never mutate `ref.current` during rendering; only in event handlers or useEffect."
    },
    "useContext": {
        "what_it_is": "A React Hook subscribing to shared state across the entire component tree without prop drilling.",
        "simple_analogy": "Think of useContext like a loudspeaker in a school! When the principal makes an announcement ('Dark Mode is ON!'), every classroom hears it instantly!",
        "what_happens_on_screen": "Theme colors, logged-in user names, and shopping carts update everywhere at once.",
        "what_if_removed": "You have to pass settings manually through 20 layers of components by hand.",
        "why_it_works": "React subscribes the component to context changes and triggers updates when Provider value changes.",
        "best_practices": "Split contexts by topic (UserContext, ThemeContext) so components don't over-render."
    },
    "async_await": {
        "what_it_is": "Syntactic sugar for writing asynchronous Promise code sequentially.",
        "simple_analogy": "Think of async/await like ordering food at a restaurant! You order, chat with your friends, and when the chef rings the bell ('await'), your food is ready!",
        "what_happens_on_screen": "Lets data load smoothly in the background without freezing the screen.",
        "what_if_removed": "The user interface would freeze like ice while waiting for the internet.",
        "why_it_works": "Yields execution back to the browser's event loop until the Promise resolves.",
        "best_practices": "Always wrap await calls in try...catch blocks to handle network errors."
    },
    "import": {
        "what_it_is": "Brings tools, functions, or components from other files into this file.",
        "simple_analogy": "Think of import like borrowing a toy from your friend's toy box! You say: 'Hey, let me borrow your red racecar for this race!'",
        "what_happens_on_screen": "Allows this file to use beautiful buttons, icons, or helpers built in other files.",
        "what_if_removed": "The file crashes with an error saying: 'I don't know what this tool is!'",
        "why_it_works": "The JavaScript module loader links the exported symbol to this file's scope.",
        "best_practices": "Keep imports organized at the very top of the file."
    },
    "export": {
        "what_it_is": "Makes functions, components, or variables available for other files to borrow.",
        "simple_analogy": "Think of export like putting your favorite toy on the sharing shelf so your friends can play with it too!",
        "what_happens_on_screen": "Allows other pages in the app to show this component.",
        "what_if_removed": "Other files cannot see or use this code.",
        "why_it_works": "Exposes the symbol in the module's public export table.",
        "best_practices": "Use named exports for utilities and default exports for main page components."
    }
}

PYTHON_KNOWLEDGE: Dict[str, Dict[str, str]] = {
    "function": {
        "what_it_is": "A reusable block of code that accepts inputs and returns an answer.",
        "simple_analogy": "Think of a function like a smoothie blender! You toss in bananas and milk (inputs), press the button, and out pours a delicious smoothie (output)!",
        "what_happens_on_screen": "Computes calculations and processes data behind the scenes.",
        "what_if_removed": "You have to copy-paste the exact same calculation everywhere by hand.",
        "why_it_works": "Python allocates a local stack frame in memory and executes instructions when called.",
        "best_practices": "Keep functions small, cohesive, and easy to test."
    },
    "def": {
        "what_it_is": "Defines a new named function (a reusable recipe of instructions).",
        "simple_analogy": "Think of `def` like teaching a robot helper a new recipe! You say: 'Robot, here is how to make pancakes! Whenever I say pancakes, do these 3 steps!'",
        "what_happens_on_screen": "Prepares code so it can be called whenever needed with different inputs.",
        "what_if_removed": "You would have to re-type the exact same instructions hundreds of times everywhere.",
        "why_it_works": "Python creates a function object in memory and binds it to the function name.",
        "best_practices": "Give functions clear action names like `calculate_total()` or `save_user()`."
    },
    "class": {
        "what_it_is": "A blueprint for creating objects that bundle data and actions together.",
        "simple_analogy": "Think of a `class` like a cookie cutter! The cookie cutter is the blueprint, and every delicious cookie you stamp out is an object!",
        "what_happens_on_screen": "Organizes complex data (like a Player, Car, or User Account) into structured items.",
        "what_if_removed": "Variables and functions get scattered with no clear organization.",
        "why_it_works": "Instantiating a class invokes `__init__` to build an instance object with its own state.",
        "best_practices": "Keep classes focused on one responsibility."
    },
    "decorator": {
        "what_it_is": "A metaprogramming wrapper (`@decorator`) that adds superpowers to a function.",
        "simple_analogy": "Think of a decorator like putting a superhero cape onto your toy robot! The robot does the same tricks, but now it can fly!",
        "what_happens_on_screen": "Automatically checks logins, logs messages, or measures speed before running the function.",
        "what_if_removed": "You have to write security and logging checks inside every function manually.",
        "why_it_works": "Syntactic sugar for `func = decorator(func)`.",
        "best_practices": "Always use `functools.wraps` inside your decorator wrapper."
    },
    "type_hints": {
        "what_it_is": "Labels specifying what kind of data is expected (e.g. `name: str, age: int`).",
        "simple_analogy": "Think of type hints like shape sorters for babies! The circle block only goes in the circle hole, so nobody puts a square in by mistake!",
        "what_happens_on_screen": "Prevents subtle bugs and helps code editors autocomplete variables.",
        "what_if_removed": "Someone might accidentally pass words where numbers were expected and crash the app.",
        "why_it_works": "Ignored at runtime, but verified statically by mypy and IDE analyzers.",
        "best_practices": "Annotate function parameters and return types."
    },
    "asyncio": {
        "what_it_is": "Framework for running many tasks concurrently without blocking.",
        "simple_analogy": "Think of asyncio like an octopus chef cooking 8 pots of soup at once! While one pot is boiling, the chef chops vegetables for the next pot!",
        "what_happens_on_screen": "Handles thousands of user requests at the exact same second without freezing.",
        "what_if_removed": "The server can only serve one customer at a time while everyone else waits in line.",
        "why_it_works": "Cooperative single-threaded event loop yielding control on `await`.",
        "best_practices": "Never execute blocking CPU-heavy calculations in the event loop."
    },
    "if_name_main": {
        "what_it_is": "A guard condition `if __name__ == '__main__':` checking if the script was run directly.",
        "simple_analogy": "Think of this like a sign on a toy racecar: 'Only start the engine if someone presses the main START button, not when it is sitting inside the toy box!'",
        "what_happens_on_screen": "Runs the main program if executed from terminal, but stays quiet if imported as a library helper.",
        "what_if_removed": "The script might accidentally run tests or print things whenever another file tries to borrow a helper function.",
        "why_it_works": "Python sets `__name__` to `'__main__'` only when the file is the direct entry point.",
        "best_practices": "Always wrap script execution in `if __name__ == '__main__': main()`."
    }
}

DOCKER_KNOWLEDGE: Dict[str, Dict[str, str]] = {
    "FROM": {
        "what_it_is": "Specifies the starting foundation image for the container.",
        "simple_analogy": "Think of FROM like picking the starter cake mix or base Lego foundation board before adding your own toppings!",
        "what_happens_on_screen": "Downloads an official pre-built Linux or Python system to build on.",
        "what_if_removed": "Docker has no operating system or foundation to build your app on and halts immediately.",
        "why_it_works": "Pulls base image filesystem layers from Docker Hub.",
        "best_practices": "Use small, specific base images like `python:3.12-slim`."
    },
    "WORKDIR": {
        "what_it_is": "Sets the active folder inside the container for all subsequent commands.",
        "simple_analogy": "Think of WORKDIR like walking into your bedroom and closing the door so all your toys stay in one clean room!",
        "what_happens_on_screen": "Keeps all application files organized inside `/app` instead of polluting the root system.",
        "what_if_removed": "Files get dumped into the messy root folder of the container.",
        "why_it_works": "Sets the default working directory for RUN, COPY, and CMD instructions.",
        "best_practices": "Always use an absolute path like `/app`."
    },
    "COPY": {
        "what_it_is": "Copies files from your computer into the container.",
        "simple_analogy": "Think of COPY like packing your backpack with your schoolbooks and bringing them into the classroom!",
        "what_happens_on_screen": "Transfers code files into the container so it can run them.",
        "what_if_removed": "The container has no code to run!",
        "why_it_works": "Creates an image layer containing your local files.",
        "best_practices": "Copy requirements.txt before copying source code to take advantage of layer caching."
    },
    "RUN": {
        "what_it_is": "Runs commands during build time (like installing libraries).",
        "simple_analogy": "Think of RUN like baking the cake in the oven so it is ready to eat later!",
        "what_happens_on_screen": "Downloads and installs necessary packages.",
        "what_if_removed": "The container won't have the libraries it needs to run your code.",
        "why_it_works": "Executes shell commands and saves the resulting filesystem state.",
        "best_practices": "Combine related commands with `&&` to keep image size small."
    },
    "EXPOSE": {
        "what_it_is": "Documents the network port the container listens on.",
        "simple_analogy": "Think of EXPOSE like painting a room number on a door so visitors know which door to knock on!",
        "what_happens_on_screen": "Tells operators which port (like 8000 or 3000) connects to the web server.",
        "what_if_removed": "People won't easily know which port the server is listening to.",
        "why_it_works": "Serves as runtime and documentation metadata.",
        "best_practices": "Always document exposed ports."
    },
    "ENTRYPOINT": {
        "what_it_is": "Configures the container to run as a fixed executable.",
        "simple_analogy": "Think of ENTRYPOINT like the steering wheel of a car—it decides the default journey!",
        "what_happens_on_screen": "Launches the main process whenever the container turns on.",
        "what_if_removed": "The container relies solely on default shell commands.",
        "why_it_works": "Passes CLI arguments directly to the entrypoint binary.",
        "best_practices": "Use JSON array format: `ENTRYPOINT [\"python\", \"app.py\"]`."
    },
    "CMD": {
        "what_it_is": "The default command executed when the container starts running.",
        "simple_analogy": "Think of CMD like pressing the 'Power' button on a racecar when the race starts!",
        "what_happens_on_screen": "Starts your web server or program.",
        "what_if_removed": "The container starts and immediately shuts down because it has nothing to do.",
        "why_it_works": "Provides default execution parameters to the container engine.",
        "best_practices": "Use JSON array format: `CMD [\"python\", \"server.py\"]`."
    }
}

SHELL_KNOWLEDGE: Dict[str, Dict[str, str]] = {
    "shebang": {
        "what_it_is": "The first line `#!/bin/bash` telling the computer which shell program to use.",
        "simple_analogy": "Think of the shebang like an address label on an envelope telling the mail carrier which language to read!",
        "what_happens_on_screen": "Ensures the script runs with Bash even if clicked or run from another shell.",
        "what_if_removed": "The computer might run the script with the wrong program and get confused.",
        "why_it_works": "The OS kernel reads magic bytes 0x23 0x21 to pick the interpreter.",
        "best_practices": "Use `#!/usr/bin/env bash` for maximum compatibility."
    },
    "strict_mode": {
        "what_it_is": "Common shell safeguard flags: `set -euo pipefail`.",
        "simple_analogy": "Think of strict mode like a safety helmet and seatbelt for your script! If any tiny thing goes wrong, it stops immediately so nobody gets hurt!",
        "what_happens_on_screen": "Stops the script immediately if any error happens so broken half-finished files aren't created.",
        "what_if_removed": "The script might keep running even if files are missing and corrupt data.",
        "why_it_works": "Enforces immediate exit on command error (`-e`) and unset variables (`-u`).",
        "best_practices": "Place `set -euo pipefail` at the start of every production shell script."
    },
    "pipe": {
        "what_it_is": "The pipe operator (`|`) sending output of one command into another.",
        "simple_analogy": "Think of a pipe like a water slide! Water slides out of one pool straight into the next slide!",
        "what_happens_on_screen": "Chains commands together in one clean line.",
        "what_if_removed": "You have to save intermediate results into temporary files.",
        "why_it_works": "Connects standard output (stdout) to standard input (stdin) via OS memory buffer.",
        "best_practices": "Use `set -o pipefail` to catch errors inside pipes."
    }
}
