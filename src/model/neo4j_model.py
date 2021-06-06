import logging

import maya
from graphql import GraphQLError
from py2neo import Graph
from py2neo.ogm import GraphObject, Property, RelatedTo
from sqlalchemy import Column, String


graph = Graph(
    host="172.28.128.14",
    port="7687",
    user="neo4j",
    password="123456",
)


class BaseModel(GraphObject):
    """
    Implements some basic functions to guarantee some standard functionality
    across all models. The main purpose here is also to compensate for some
    missing basic features that we expected from GraphObjects, and improve the
    way we interact with them.
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @property
    def all(self):
        return self.match(graph)

    def save(self):
        graph.push(self)


class Node(BaseModel):
    __primarykey__ = 'id'
    label = Column(String)
    id = Column(String)
    name = Column(String)
    address = Column(String)
    worker_number = Column(String)

    def fetch_all(self):
        exec_cmd = 'match (n) where %s return n'
        tmp_value = []
        if self.id:
            tmp_value.append('n.id="%s"' % self.id)

        if self.label:
            tmp_value.append('n.label="%s"' % self.label)

        if self.name:
            tmp_value.append('n.name="%s"' % self.name)

        if self.address:
            tmp_value.append('n.address="%s"' % self.address)

        if self.worker_number:
            tmp_value.append('n.label="%s"' % self.worker_number)

        if tmp_value:
            logging.info(exec_cmd % " and ".join(tmp_value))
            return graph.run(
                exec_cmd % " and ".join(tmp_value)).data()
        else:
            return tmp_value

    def fetch_id(self):
        return graph.run('match (n) where n.id="%s" return n' % self.id).data()

    def fetch_name(self):
        return \
            graph.run('match (n) where n.name="%s" return n' % self.name).data()

    def fetch_label(self):
        return \
            graph.run(
                'match (n) where n.label="%s" return n' % self.label).data()

    def fetch_address(self):
        return \
            graph.run(
                'match (n) where n.address="%s" return n' % self.address).data()

    def fetch_worker_number(self):
        return \
            graph.run(
                'match (n) where n.worker_number="%s" return n' %
                self.worker_number).data()

    def format_create_cmd(self):
        return 'CREATE (%s:%s ' \
            '{ id:"%s",name:"%s",address:"%s",worker_number:"%s" })' % (
                self.name,
                self.label,
                self.id,
                self.name,
                self.address,
                self.worker_number
            )

    def format_check_exist_cmd(self):
        return 'match (n) where n.id="%s" return n' % self.id

    def commit(self):
        check_exist_result = graph.run(self.format_check_exist_cmd()).data()
        if not check_exist_result:
            graph.run(self.format_create_cmd())
        else:
            logging.warning("node %s is existed." % self.id)


class Graph(BaseModel):
    src_label = Column(String)
    src_id = Column(String)
    tar_label = Column(String)
    tar_id = Column(String)
    relationship_name = Column(String)

    def fetch(self):
        customer = self.match(graph, self.id).first()
        if customer is None:
            raise GraphQLError(
                f'"{self.id}" has not been found in our customers list.')

        return customer

    def format_create_cmd(self):
        return 'match (n:%s{id:"%s"}),(m:%s{id:"%s"}) ' \
            'create (n)-[r:%s]->(m) return r;' % (
                self.src_label,
                self.src_id,
                self.tar_label,
                self.tar_id,
                self.relationship_name
            )

    def format_check_exist_cmd(self):
        return 'match (n:%s{id:"%s"})-[r:%s]->(m:%s{id:"%s"}) return r;' % (
                   self.src_label,
                   self.src_id,
                   self.relationship_name,
                   self.tar_label,
                   self.tar_id
               )

    def commit(self):
        check_exist_result = graph.run(self.format_check_exist_cmd()).data()
        print(check_exist_result)
        if not check_exist_result:
            graph.run(self.format_create_cmd())
        else:
            logging.warning("relationship %s is existed." %
                            self.relationship_name)
