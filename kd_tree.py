from dataclasses import dataclass
from typing import Optional, List

#classe que representa um ponto geográfico com nome, endereço e coordenadas
@dataclass
class Point:
    name: str
    address: str
    lat: float
    lon: float

#nó da kd-tree que armazena um ponto, o eixo de divisão e referências para filhos esquerdo e direito
@dataclass
class KDNode:
    point: Point
    axis: int
    left: Optional["KDNode"] = None
    right: Optional["KDNode"] = None

#estrutura kd-tree construída a partir de uma lista de pontos para permitir buscas espaciais eficientes
class KDTree:
    #inicializa a kd-tree filtrando pontos inválidos e construindo a árvore recursivamente
    def __init__(self, points: List[Point]):
        valid_points = [
            item
            for item in points
            if item.lat is not None
            and item.lon is not None
        ]

        self.root = self._create_tree(
            valid_points,
            0,
        )
    #constrói recursivamente a kd-tree escolhendo a mediana dos pontos com base no eixo atual
    def _create_tree(
        self,
        values: List[Point],
        level: int,
    ) -> Optional[KDNode]:
        if len(values) == 0:
            return None
        current_axis = level % 2
        sorted_points = sorted(
            values,
            key=lambda item: (
                item.lat
                if current_axis == 0
                else item.lon
            ),
        )
        middle_index = len(sorted_points) // 2
        middle_point = sorted_points[middle_index]
        left_branch = self._create_tree(
            sorted_points[:middle_index],
            level + 1,
        )
        right_branch = self._create_tree(
            sorted_points[middle_index + 1:],
            level + 1,
        )
        return KDNode(
            point=middle_point,
            axis=current_axis,
            left=left_branch,
            right=right_branch,
        )

    #retorna o número total de nós presentes na kd-tree.
    def __len__(self):
        def node_count(current_node):
            if current_node is None:
                return 0
            return (
                1
                + node_count(current_node.left)
                + node_count(current_node.right)
            )
        return node_count(self.root)