from typing import Callable, Dict, Union

from nicegui import background_tasks, helpers, ui


class RouterFrame(ui.element, component='router_frame.js'):
    pass

class Router:

    def __init__(self) -> None:
        self.routes: Dict[str, Callable] = {}
        self.content: ui.element = None

    def add(self, path: str):
        # ensure that path starts with a "/" Note: It might also be an Option to modify the path variable by simple appending the "/" at the beginning in this case 
        if path.startswith("/") == False:
            raise Warning('When adding a path to the Router it must begin with a "/" for the router to work correctly')
        if path.endswith("/") == False:
            raise Warning('When adding a path to the Router it must end with a "/" for the router to work correctly')
        def decorator(func: Callable):
            self.routes[path] = func
            return func
        return decorator

    def open(self, target: Union[Callable, str]) -> None:
        if isinstance(target, str):
            path = target

            builder = self.routes[path]
        else:
            path = {v: k for k, v in self.routes.items()}[target]
            builder = target

        async def build() -> None:
            with self.content:
                await ui.run_javascript(f'''
                    if (window.location.pathname !== "{path}") {{
                        history.pushState({{page: "{path}"}}, "", "{path}");
                    }}
                ''')
                result = builder()
                if helpers.is_coroutine_function(builder):
                    await result
        self.content.clear()
        background_tasks.create(build())

    def frame(self) -> ui.element:
        self.content = RouterFrame().on('open', lambda e: self.open(e.args))
        return self.content


ROUTER = Router()