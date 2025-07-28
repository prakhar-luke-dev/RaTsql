# -*- coding: utf-8 -*-
# Project : 
# File    : utils.py
# Author  : prakhar-luke-dev
# Email   : prakhar.luke.dev@gmail.com
# Time    : 7/28/25 3:29 PM

def save_graph_to_file(runnable_graph, output_file_path):
    file_path = f"graph_visuals/{output_file_path}.png"
    png_bytes = runnable_graph.get_graph().draw_mermaid_png()
    with open(file_path, 'wb') as file:
        file.write(png_bytes)

