from typing import List, Union, Callable


Element = Union[str, 'Block', 'Span', Callable[['Element'], 'Element']]


class String:
    def __init__(self, value):
        self.value = value
    
    def render(self, indent=0):
        return ('  '*indent) + self.value
    
    def __repr__(self):
        return self.value


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
    
    def push(self, element: Element):
        if type(element) is Block:
            raise Exception("spans cannot contain blocks")

        Container.push(self, element)
    
    
    def render(self, indent=0):
        indentation = '  '*indent
        rendered = ""
        
        for idx, element in enumerate(self.elements):
            if type(element) is Block:
                raise Exception("spans cannot contain blocks")
            
            rendered += element.render()
        
        if self.action is not None:
            rendered = self.action(rendered)
            
        return indentation + rendered


class Block(Container):
    
    def __init__(self, prefix=None, suffix=None):
        super().__init__()
        self.prefix = prefix
        self.suffix = suffix

    
    def render(self, indent=0):
        indentation = '  '*indent
        rendered = ""
        
        if self.prefix is not None:
            rendered += f"{indentation}{self.prefix}\n"
        
        rendered += f"\n".join([_.render(indent=indent+1) for _ in self.elements])

        if self.suffix is not None:
            rendered += f"\n{indentation}{self.suffix}"
                       
        if self.action is not None:
            rendered = self.action(rendered)

        return rendered