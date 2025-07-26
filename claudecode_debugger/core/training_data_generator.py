"""Generate training data for the ML classifier."""

import random
from typing import Any, Dict, List, Optional

from .advanced_detector import ErrorCategory
from .ml_classifier import TrainingExample


class TrainingDataGenerator:
    """Generate synthetic training data for error classification."""

    def __init__(self):
        """Initialize the training data generator."""
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize error templates for each category."""
        return {
            ErrorCategory.TYPESCRIPT.value: [
                {
                    "template": "error TS{code}: {message} at {file}:{line}:{col}",
                    "severity": "high",
                    "variations": {
                        "code": ["2322", "2345", "2339", "2532", "2304"],
                        "message": [
                            "Type 'string' is not assignable to type 'number'",
                            "Argument of type 'undefined' is not assignable to parameter",
                            "Property 'length' does not exist on type 'number'",
                            "Object is possibly 'undefined'",
                            "Cannot find name 'React'",
                        ],
                        "file": ["src/app.ts", "lib/utils.ts", "components/Button.tsx"],
                        "line": range(1, 200),
                        "col": range(1, 80),
                    },
                },
                {
                    "template": "Cannot find module '{module}' or its corresponding type declarations.",
                    "severity": "high",
                    "variations": {
                        "module": [
                            "react",
                            "@types/node",
                            "./config",
                            "../utils/helpers",
                        ]
                    },
                },
            ],
            ErrorCategory.JAVASCRIPT.value: [
                {
                    "template": "{error_type}: {message}\n    at {function} ({file}:{line}:{col})",
                    "severity": "high",
                    "variations": {
                        "error_type": ["TypeError", "ReferenceError", "SyntaxError"],
                        "message": [
                            "Cannot read property 'map' of undefined",
                            "undefined is not a function",
                            "Unexpected token '}'",
                        ],
                        "function": [
                            "Array.map",
                            "Object.keys",
                            "handleClick",
                            "render",
                        ],
                        "file": ["app.js", "index.js", "utils.js"],
                        "line": range(1, 500),
                        "col": range(1, 120),
                    },
                },
                {
                    "template": "Uncaught Error: {message}\n{stack_trace}",
                    "severity": "high",
                    "variations": {
                        "message": [
                            "Invalid hook call",
                            "Maximum update depth exceeded",
                            "Network request failed",
                        ],
                        "stack_trace": [
                            "    at throwInvalidHookError (react-dom.development.js:14906)\n    at useContext (react.development.js:1504)",
                            "    at checkForNestedUpdates (react-dom.development.js:23093)\n    at scheduleUpdateOnFiber (react-dom.development.js:21169)",
                            "    at XMLHttpRequest.xhr.onerror (fetch.js:89)",
                        ],
                    },
                },
            ],
            ErrorCategory.PYTHON.value: [
                {
                    "template": 'Traceback (most recent call last):\n  File "{file}", line {line}, in {function}\n    {code}\n{error_type}: {message}',
                    "severity": "high",
                    "variations": {
                        "file": ["main.py", "app.py", "utils.py", "models.py"],
                        "line": range(1, 300),
                        "function": ["main", "process_data", "calculate", "__init__"],
                        "code": [
                            'result = data["key"]',
                            "import missing_module",
                            "x = 1 / 0",
                            "list_item = my_list[10]",
                        ],
                        "error_type": [
                            "KeyError",
                            "ImportError",
                            "ZeroDivisionError",
                            "IndexError",
                        ],
                        "message": [
                            "'key'",
                            "No module named 'missing_module'",
                            "division by zero",
                            "list index out of range",
                        ],
                    },
                },
                {
                    "template": "asyncio.TimeoutError: {message}",
                    "severity": "medium",
                    "variations": {
                        "message": [
                            "Operation timed out after 30.0 seconds",
                            "Future didn't complete within 60 seconds",
                        ]
                    },
                },
            ],
            ErrorCategory.MEMORY.value: [
                {
                    "template": "FATAL ERROR: {message}\n{details}",
                    "severity": "critical",
                    "variations": {
                        "message": [
                            "Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory",
                            "CALL_AND_RETRY_LAST Allocation failed - JavaScript heap out of memory",
                            "Reached heap limit Allocation failed - JavaScript heap out of memory",
                        ],
                        "details": [
                            "1: 0x10130e5e5 node::Abort() [/usr/local/bin/node]\n2: 0x10130e76f node::OnFatalError(char const*, char const*) [/usr/local/bin/node]",
                            "<--- Last few GCs --->\n[28729:0x102801000]    30065 ms: Mark-sweep 1387.0 (1420.0) -> 1386.9 (1421.0) MB",
                            "Security context: 0x38e8c7b9e6e1 <JSObject>\n    1: _send [internal/child_process.js:~778]",
                        ],
                    },
                },
                {
                    "template": "java.lang.OutOfMemoryError: {space}",
                    "severity": "critical",
                    "variations": {
                        "space": [
                            "Java heap space",
                            "GC overhead limit exceeded",
                            "Metaspace",
                        ]
                    },
                },
            ],
            ErrorCategory.NETWORK.value: [
                {
                    "template": "Access to fetch at '{url}' from origin '{origin}' has been blocked by CORS policy: {reason}",
                    "severity": "medium",
                    "variations": {
                        "url": [
                            "https://api.example.com/data",
                            "http://localhost:3001/api/users",
                        ],
                        "origin": ["http://localhost:3000", "https://myapp.com"],
                        "reason": [
                            "No 'Access-Control-Allow-Origin' header is present on the requested resource",
                            "The request client is not a secure context",
                            "Response to preflight request doesn't pass access control check",
                        ],
                    },
                },
                {
                    "template": "Error: {error_code} {message}",
                    "severity": "medium",
                    "variations": {
                        "error_code": ["ECONNREFUSED", "ETIMEDOUT", "ENOTFOUND"],
                        "message": [
                            "connect ECONNREFUSED 127.0.0.1:3000",
                            "timeout of 5000ms exceeded",
                            "getaddrinfo ENOTFOUND api.example.com",
                        ],
                    },
                },
            ],
            ErrorCategory.REACT.value: [
                {
                    "template": "Error: {message}\n{component_stack}",
                    "severity": "high",
                    "variations": {
                        "message": [
                            "Invalid hook call. Hooks can only be called inside of the body of a function component",
                            "Too many re-renders. React limits the number of renders to prevent an infinite loop",
                            "Objects are not valid as a React child (found: object with keys {user, posts})",
                        ],
                        "component_stack": [
                            "    in App (at src/index.js:7)\n    in StrictMode (at src/index.js:6)",
                            "    in UserProfile (at Dashboard.js:25)\n    in Dashboard (at App.js:15)",
                            "    in div (at Layout.js:10)\n    in Layout (at App.js:8)",
                        ],
                    },
                }
            ],
            ErrorCategory.DATABASE.value: [
                {
                    "template": "{db_error}: {message}\nSQL: {query}",
                    "severity": "high",
                    "variations": {
                        "db_error": [
                            "psycopg2.errors.UndefinedTable",
                            "mysql.connector.errors.ProgrammingError",
                            "sqlite3.OperationalError",
                        ],
                        "message": [
                            'relation "users" does not exist',
                            "1054 (42S22): Unknown column 'email' in 'field list'",
                            "no such table: products",
                        ],
                        "query": [
                            "SELECT * FROM users WHERE id = %s",
                            "INSERT INTO orders (user_id, total) VALUES (?, ?)",
                            "UPDATE products SET stock = stock - 1 WHERE id = ?",
                        ],
                    },
                }
            ],
            ErrorCategory.DOCKER.value: [
                {
                    "template": "docker: Error response from daemon: {message}",
                    "severity": "high",
                    "variations": {
                        "message": [
                            "pull access denied for myapp, repository does not exist or may require 'docker login'",
                            "driver failed programming external connectivity on endpoint webapp",
                            'Conflict. The container name "/redis" is already in use',
                        ]
                    },
                },
                {
                    "template": "ERROR: Service '{service}' failed to build: {reason}",
                    "severity": "high",
                    "variations": {
                        "service": ["web", "db", "redis", "nginx"],
                        "reason": [
                            "The command '/bin/sh -c npm install' returned a non-zero code: 1",
                            "COPY failed: stat /var/lib/docker/tmp/docker-builder123/app: no such file or directory",
                            "pull access denied for node:18-alpine, repository does not exist",
                        ],
                    },
                },
            ],
            ErrorCategory.CICD.value: [
                {
                    "template": "##[error]{message}\n{details}",
                    "severity": "high",
                    "variations": {
                        "message": [
                            "Process completed with exit code 1",
                            "The operation was canceled",
                            "Resource not accessible by integration",
                        ],
                        "details": [
                            "npm ERR! Test failed. See above for more details.",
                            "Error: The process '/usr/bin/git' failed with exit code 128",
                            "Error: HttpError: Not Found",
                        ],
                    },
                }
            ],
        }

    def generate_examples(
        self, count: int = 1000, categories: Optional[List[str]] = None
    ) -> List[TrainingExample]:
        """
        Generate training examples.

        Args:
            count: Number of examples to generate.
            categories: Specific categories to generate (None for all).

        Returns:
            List of training examples.
        """
        examples = []

        if categories is None:
            categories = list(self.templates.keys())

        for _ in range(count):
            # Select category (with some multi-label examples)
            if random.random() < 0.2:  # 20% chance of multi-label
                selected_categories = random.sample(
                    categories, k=min(2, len(categories))
                )
            else:
                selected_categories = [random.choice(categories)]

            # Generate error text
            error_text = ""
            severity = "medium"

            for category in selected_categories:
                if category in self.templates:
                    template_data = random.choice(self.templates[category])
                    error_text += self._generate_from_template(template_data) + "\n\n"
                    # Use highest severity
                    if template_data["severity"] == "critical":
                        severity = "critical"
                    elif template_data["severity"] == "high" and severity != "critical":
                        severity = "high"

            # Add some noise
            if random.random() < 0.3:
                error_text = self._add_noise(error_text)

            example = TrainingExample(
                text=error_text.strip(),
                categories=selected_categories,
                severity=severity,
                metadata={"synthetic": True},
            )
            examples.append(example)

        return examples

    def _generate_from_template(self, template_data: Dict[str, Any]) -> str:
        """Generate error text from a template."""
        template = template_data["template"]
        variations = template_data.get("variations", {})

        # Replace placeholders
        for key, values in variations.items():
            placeholder = f"{{{key}}}"
            if placeholder in template:
                if isinstance(values, range):
                    value = str(random.choice(list(values)))
                elif isinstance(values, list):
                    value = random.choice(values)
                else:
                    value = str(values)
                template = template.replace(placeholder, value)

        return template

    def _add_noise(self, text: str) -> str:
        """Add realistic noise to error text."""
        noise_types = [
            lambda t: f"[2023-10-{random.randint(1,30):02d} {random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}] "
            + t,
            lambda t: f"ERROR: " + t,
            lambda t: f"[{random.randint(1000,9999)}] " + t,
            lambda t: t
            + f"\nNode.js v{random.randint(14,20)}.{random.randint(0,10)}.{random.randint(0,5)}",
            lambda t: f"    at process._tickCallback (internal/process/next_tick.js:{random.randint(50,200)}:{random.randint(1,50)})\n"
            + t,
        ]

        if random.random() < 0.5:
            noise_func = random.choice(noise_types)
            text = noise_func(text)

        return text

    def generate_real_world_examples(self) -> List[TrainingExample]:
        """Generate examples that closely mimic real-world errors."""
        examples = []

        # Real-world TypeScript error
        examples.append(
            TrainingExample(
                text="""src/components/UserList.tsx:45:5 - error TS2322: Type 'string[]' is not assignable to type 'User[]'.
  Type 'string' is not assignable to type 'User'.

45     setUsers(response.data.names);
       ~~~~~~~~

  src/components/UserList.tsx:15:3
    15   setUsers: (users: User[]) => void;
         ~~~~~~~~
    The expected type comes from property 'setUsers' which is declared here on type 'UserListProps'

Found 1 error in src/components/UserList.tsx:45""",
                categories=[ErrorCategory.TYPESCRIPT.value],
                severity="high",
            )
        )

        # Real-world Python error with async
        examples.append(
            TrainingExample(
                text="""Traceback (most recent call last):
  File "/app/src/services/data_processor.py", line 127, in process_batch
    results = await asyncio.gather(*tasks)
  File "/usr/local/lib/python3.9/asyncio/tasks.py", line 349, in gather
    return await _gather(*tasks, loop=loop)
  File "/app/src/services/api_client.py", line 89, in fetch_data
    async with session.get(url, timeout=30) as response:
  File "/usr/local/lib/python3.9/site-packages/aiohttp/client.py", line 1117,
    in __aenter__
    self._resp = await self._coro
  File "/usr/local/lib/python3.9/site-packages/aiohttp/client.py", line 520, in _request
    conn = await self._connector.connect(
asyncio.TimeoutError: Timeout context manager should be used inside a task""",
                categories=[ErrorCategory.PYTHON.value, ErrorCategory.ASYNC.value],
                severity="high",
            )
        )

        # Real-world memory error
        examples.append(
            TrainingExample(
                text="""<--- Last few GCs --->

[28729:0x102801000]    30065 ms: Mark-sweep 1387.0 (1420.0) -> 1386.9 (1421.0) MB,
    184.9 / 0.0 ms  (average mu = 0.112,
    current mu = 0.011) allocation failure scavenge might not succeed
[28729:0x102801000]    30253 ms: Mark-sweep 1387.9 (1421.0) -> 1387.8 (1421.5) MB,
    187.3 / 0.0 ms  (average mu = 0.060,
    current mu = 0.003) allocation failure scavenge might not succeed


<--- JS stacktrace --->

==== JS stack trace =========================================

    0: ExitFrame [pc: 0x100a0bd99]
Security context: 0x38e8c7b9e6e1 <JSObject>
    1: _send [internal/child_process.js:~778] [pc=0x3d2f828bfc55](this=0x38e84885cf51 <ChildProcess map = 0x38e814896361>,
    message=0x38e848864ae1 <Object map = 0x38e8148a1fe1>,
    handle=0x38e8ba8026f1 <undefined>,
    options=0x38e848864b41 <Object map = 0x38e814882f11>,
    callback=0x38e8ba8026f1 <undefined>)
    2: send [internal/child_process.js:~...

FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory
 1: 0x10130e5e5 node::Abort() [/usr/local/bin/node]
 2: 0x10130e76f node::OnFatalError(char const*, char const*) [/usr/local/bin/node]""",
                categories=[ErrorCategory.MEMORY.value, ErrorCategory.JAVASCRIPT.value],
                severity="critical",
            )
        )

        # Real-world Docker + CI/CD error
        examples.append(
            TrainingExample(
                text="""Step 8/12 : RUN npm install
 ---> Running in 4f8b9c7e3a2d
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
npm ERR!
npm ERR! While resolving: myapp@1.0.0
npm ERR! Found: react@18.2.0
npm ERR! node_modules/react
npm ERR!   react@"^18.2.0" from the root project
npm ERR!
npm ERR! Could not resolve dependency:
npm ERR! peer react@"^16.8.0 || ^17.0.0" from react-widget@2.5.1
npm ERR! node_modules/react-widget
npm ERR!   react-widget@"^2.5.1" from the root project

The command '/bin/sh -c npm install' returned a non-zero code: 1
##[error]Process completed with exit code 1.
##[error]Docker build failed with exit code 1""",
                categories=[
                    ErrorCategory.DOCKER.value,
                    ErrorCategory.BUILD.value,
                    ErrorCategory.CICD.value,
                ],
                severity="high",
            )
        )

        return examples

    def export_training_data(
        self, examples: List[TrainingExample], output_file: str = "training_data.json"
    ):
        """Export training examples to JSON file."""
        import json

        data = []
        for example in examples:
            data.append(
                {
                    "text": example.text,
                    "categories": example.categories,
                    "severity": example.severity,
                    "metadata": example.metadata or {},
                }
            )

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Exported {len(examples)} examples to {output_file}")

    def import_training_data(self, input_file: str) -> List[TrainingExample]:
        """Import training examples from JSON file."""
        import json

        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        examples = []
        for item in data:
            example = TrainingExample(
                text=item["text"],
                categories=item["categories"],
                severity=item["severity"],
                metadata=item.get("metadata"),
            )
            examples.append(example)

        return examples
