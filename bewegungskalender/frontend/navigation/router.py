from typing import Callable, Dict, Union

from nicegui import binding, background_tasks, helpers, ui

from bewegungskalender.frontend.main.theme import Theme


class RouterFrame(ui.element, component='router_frame.js'):
    pass

class Page:
    def __init__(self,func: Callable,path: str) -> None:
        self.func: Callable = func
        self.path: str = path

class Router:

    def __init__(self) -> None:
        self.routes: Dict[str, Page] = {}
        self.current_page: Page | None = None

    def add(self, path: str):
        # ensure that path starts with a "/" Note: It might also be an Option to modify the path variable by simple appending the "/" at the beginning in this case 
        if path.startswith("/") == False:
            raise Warning('When adding a path to the Router it must begin with a "/" for the router to work correctly')
       
        def decorator(func: Callable):
            self.routes[path] = Page(func,path)
            return func
        return decorator

    def open(self, target: Union[Callable, str]) -> None:
        if isinstance(target, str):
            
            # when target is unknown we reroute to "/" as default.
            # TODO: It might be wise to have some way for a default value or perhaps an erorr page to be passed somehow to the router
            if self.routes.get(target) == None:
                target = "/"
            builder = self.routes[target].func
            path = target
            self.current_page = self.routes[path]


        else:
            path = {v.func: k for k, v in self.routes.items()}[target]
            builder = self.routes[path].func
            self.current_page = self.routes[path]

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

        ui.run_javascript("emitEvent('router_open_page');")

    def frame(self) -> ui.element:
        self.content = RouterFrame().on('open', lambda e: self.open(e.args))
        return self.content


ROUTER = Router()