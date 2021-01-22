from typing import List, Union, Callable


Element = Union[str, 'Block', 'Span', Callable[['Element'], 'Element']]


class String:
    def __init__(self, value):
        self.value = value
    
    def render(self, indent=0):
        return ('  '*indent) + self.value


class Container:
    elements: List[Element]
    
    def __init__(self, action=None):
        self.action = action
        self.elements = []

    def push(self, element: Element):
        if type(element) is str:
            element = String(element)
        
        self.elements.append(element)


class Span(Container):

    def render(self, indent=0):
        rendered = "".join([_.render() for _ in self.elements])
        
        if self.action is not None:
            rendered = self.action(rendered)
            
        return ('  '*indent) + rendered


class Block(Container):
    
    def render(self, indent=0):
        rendered = f"\n{'  ' * indent}".join([_.render(indent=indent+1) for _ in self.elements])
        
        if self.action is not None:
            rendered = self.action(rendered)
        
        return rendered
        
        # actions = []
        # 
        # for element in self.elements:
        #     element_type = type(element)
        #     
        #     if element_type is str:
        #         content = ('  ' * indent).join(element.splitlines(keepends=True))
        #         rendered += actions.pop()(content) if actions else content
        #     
        #     elif element_type is Block:
        #         indent += 1
        #         rendered += "\n"
        #         content = element.render(indent=indent+1)
        #         rendered += actions.pop()(content) if actions else content
        # 
        #     elif element_type is callable:
        #         actions.append(element)
        #     
        # return rendered