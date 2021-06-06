import logging

from sqlalchemy import create_engine
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from src.model import neo4j_model


class CreateNode(graphene.Mutation):
    label = graphene.String()
    id = graphene.String()
    name = graphene.String()
    address = graphene.String()
    worker_number = graphene.String()

    class Arguments:
        label = graphene.String()
        id = graphene.String()
        name = graphene.String()
        address = graphene.String()
        worker_number = graphene.String()

    def mutate(self, info, label, id, name, address, worker_number):
        node = \
            neo4j_model.Node(
                label=label,
                id=id,
                name=name,
                address=address,
                worker_number=worker_number
            )
        node.commit()

        return CreateNode(
            label=node.label,
            id=node.id,
            name=node.name,
            address=node.address,
            worker_number=node.worker_number
        )


class CreateGraph(graphene.Mutation):
    src_label = graphene.String()
    src_id = graphene.String()
    src_name = graphene.String()
    src_address = graphene.String()
    src_worker_number = graphene.String()
    tar_label = graphene.String()
    tar_id = graphene.String()
    tar_name = graphene.String()
    tar_address = graphene.String()
    tar_worker_number = graphene.String()
    relationship_name = graphene.String()

    class Arguments:
        src_label = graphene.String()
        src_id = graphene.String()
        src_name = graphene.String()
        src_address = graphene.String()
        src_worker_number = graphene.String()
        tar_label = graphene.String()
        tar_id = graphene.String()
        tar_name = graphene.String()
        tar_address = graphene.String()
        tar_worker_number = graphene.String()
        relationship_name = graphene.String()

    def mutate(
            self,
            info,
            src_label, src_id, src_name, src_address, src_worker_number,
            tar_label, tar_id, tar_name, tar_address, tar_worker_number,
            relationship_name
    ):
        src_node = \
            neo4j_model.Node(
                label=src_label,
                id=src_id,
                name=src_name,
                address=src_address,
                worker_number=src_worker_number
            )
        src_node.commit()

        tar_node = \
            neo4j_model.Node(
                label=tar_label,
                id=tar_id,
                name=tar_name,
                address=tar_address,
                worker_number=tar_worker_number
            )
        tar_node.commit()

        relation = neo4j_model.Graph(
            src_label=src_label,
            src_id=src_id,
            tar_label=tar_label,
            tar_id=tar_id,
            relationship_name=relationship_name
        )
        relation.commit()

        return CreateGraph(
            src_label=src_label,
            src_id=src_id,
            src_name=src_name,
            src_address=src_address,
            src_worker_number=src_worker_number,
            tar_label=tar_label,
            tar_id=tar_id,
            tar_name=tar_name,
            tar_address=tar_address,
            tar_worker_number=tar_worker_number,
            relationship_name=relationship_name
        )


class NodeSchema(graphene.ObjectType):
    label = graphene.String()
    id = graphene.String()
    name = graphene.String()
    address = graphene.String()
    worker_number = graphene.String()


class NodeSchemaList(graphene.ObjectType):
    node = graphene.Field(
            lambda: NodeSchema,
            label=graphene.String(),
            id=graphene.String(),
            name=graphene.String(),
            address=graphene.String(),
            worker_number=graphene.String(),
        )

    def resolve_node(self, info):
        print(self.node)
        return self.node


class Query(graphene.ObjectType):
    nodes = \
        graphene.Field(
            lambda: NodeSchema,
            label=graphene.String(),
            id=graphene.String(),
            name=graphene.String(),
            address=graphene.String(),
            worker_number=graphene.String(),
        )

    def resolve_nodes(self, info, **args):
        label = args.get("label")
        id = args.get("id")
        name = args.get("name")
        address = args.get("address")
        worker_number = args.get("worker_number")

        node = neo4j_model.Node(
            label=label,
            id=id,
            name=name,
            address=address,
            worker_number=worker_number
        )

        fetch_result = node.fetch_all()
        return_node_list = []
        if not fetch_result:
            sub_node = NodeSchema(
                    label="",
                    id="",
                    name="",
                    address="",
                    worker_number=""
                )
            return_node_list.append(sub_node)
        else:
            for node in fetch_result:
                sub_node = NodeSchema(
                    label=node["n"].labels,
                    id=node["n"]["id"],
                    name=node["n"]["name"],
                    address=node["n"]["address"],
                    worker_number=node["n"]["worker_number"]
                )
                return_node_list.append(sub_node)
        print(return_node_list)
        return_result_list = graphene.List(NodeSchema, description="list nodes")
        print(return_node_list)
        return NodeSchemaList(
            node=return_result_list
        )


class Mutation(graphene.ObjectType):
    create_node = CreateNode.Field()
    create_graph = CreateGraph.Field()


schema = \
    graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=False)
