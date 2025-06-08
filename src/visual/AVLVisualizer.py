import networkx as nx
import matplotlib.pyplot as plt

class AVLVisualizer:
    def __init__(self, tree=None):
        self.G = nx.Graph()
        self.pos = {}
        self.labels = {}
        self.tree = tree

    def _create_node_label(self, node):
        """
        Creates node label in format 'route\nFreq: n'
        """
        if not node or not node.key:
            return ""
        
        # Route is stored in the nodes attribute of Route object (node.key)
        route = " → ".join(str(n) for n in node.key.nodes)
        return f"{route}\nFreq: {node.key.frequency}"

    def visualize(self):
        """
        Wrapper method that calls draw_tree for compatibility.
        """
        return self.draw_tree()

    def draw_tree(self):
        """
        Visualizes the AVL tree using networkx.
        
        Returns:
            matplotlib.figure.Figure: The generated figure
        """
        self.G.clear()
        self.pos.clear()
        self.labels.clear()
        
        if not self.tree:
            return plt.figure()  # Return empty figure if no tree
            
        def _build_graph(node, x=0, y=0, layer=1):
            if not node:
                return
                
            # Create current node
            node_id = id(node)
            self.G.add_node(node_id)
            self.pos[node_id] = (x, y)
            self.labels[node_id] = self._create_node_label(node)
        
            # Process left child
            if node.left:
                left_id = id(node.left)
                self.G.add_edge(node_id, left_id)
                _build_graph(node.left, x-2/layer, y-1, layer+1)
                
            # Process right child
            if node.right:
                right_id = id(node.right)
                self.G.add_edge(node_id, right_id)
                _build_graph(node.right, x+2/layer, y-1, layer+1)
        
        _build_graph(self.tree.root if self.tree else None)
        
        if not self.G.nodes():
            return plt.figure()  # Return empty figure if no nodes
            
        # Create figure with dark theme
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(15, 10))
        fig.patch.set_facecolor('#0E1117')
        ax = plt.gca()
        ax.set_facecolor('#0E1117')
        
        # Draw nodes with dark theme colors
        nx.draw_networkx_nodes(self.G, self.pos,
                             node_color='#262730',  # Dark node color
                             node_size=3000,
                             node_shape='o',
                             edgecolors='#4B4B4B',  # Dark border color
                             linewidths=2)
        
        # Draw edges with dark theme colors
        nx.draw_networkx_edges(self.G, self.pos,
                             edge_color='#4B4B4B',  # Dark edge color
                             width=1,
                             arrows=True,
                             arrowsize=20)
        
        # Draw labels with light colors
        nx.draw_networkx_labels(self.G, self.pos,
                              self.labels,
                              font_size=10,
                              font_weight='bold',
                              font_color='#FAFAFA')  # Light text color
        
        plt.title("Route Frequency AVL Tree", pad=20, fontsize=16, color='#FAFAFA')
        plt.axis('off')
        
        return fig 