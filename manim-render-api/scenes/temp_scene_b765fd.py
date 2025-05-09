from manim import *

class HelloScene(Scene):
    def construct(self):
        text = Text('Hello, world!')
        self.play(Write(text))
        self.wait(1)