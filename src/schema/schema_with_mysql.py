from sqlalchemy import create_engine
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

SQLALCHEMY_DATABASE_URI = \
    'mysql+pymysql://root:123456@172.28.128.14:3306/study?charset=utf8mb4'

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Book(Base):
    __tablename__ = 'book'
    id = Column(String, primary_key=True)
    name = Column(String)


class Paper(Base):
    __tablename__ = 'paper'
    id = Column(String, primary_key=True)
    paper_name = Column(String)
    update_time = Column(String)


class BookQuery(SQLAlchemyObjectType):
    class Meta:
        model = Book


class PaperQuery(SQLAlchemyObjectType):
    class Meta:
        model = Paper


class Query(graphene.ObjectType):
    books = \
        graphene.List(BookQuery, id=graphene.String(), name=graphene.String())
    book = \
        graphene.Field(BookQuery, id=graphene.String(), name=graphene.String())
    papers = \
        graphene.List(PaperQuery,
                      id=graphene.String(),
                      updateTime=graphene.String(),
                      paperName=graphene.String()
                      )
    paper = \
        graphene.Field(
            PaperQuery,
            id=graphene.String(),
            updateTime=graphene.String(),
            paperName=graphene.String()
            )
    test = graphene.Field(graphene.String)

    def resolve_books(self, info, **args):
        id = args.get("id")
        name = args.get("name")
        query = BookQuery.get_query(info)  # SQLAlchemy query
        if id:
            query = query.filter(Book.id == id)
        if name:
            query = query.filter(Book.name == name)
        return query.all()

    def resolve_book(self, info, **args):
        id = args.get("id")
        name = args.get("name")
        query = BookQuery.get_query(info)  # SQLAlchemy query
        if id:
            query = query.filter(Book.id == id)
        if name:
            query = query.filter(Book.name == name)
        return query.first()

    def resolve_papers(self, info, **args):
        id = args.get("id")
        update_time = args.get("updateTime")
        paper_name = args.get("paperName")
        query = PaperQuery.get_query(info)  # SQLAlchemy query
        if id:
            query = query.filter(Paper.id == id)
        if paper_name:
            query = query.filter(Paper.paper_name == paper_name)
        if update_time:
            query = query.filter(Paper.update_time == update_time)
        query = query.order_by(Paper.update_time.desc())
        return query.all()

    def resolve_paper(self, info, **args):
        id = args.get("id")
        update_time = args.get("updateTime")
        paper_name = args.get("paperName")
        query = PaperQuery.get_query(info)  # SQLAlchemy query
        if id:
            query = query.filter(Paper.id == id)
        if paper_name:
            query = query.filter(Paper.paper_name == paper_name)
        if update_time:
            query = query.filter(Paper.update_time == update_time)
        query = query.order_by(Paper.update_time.desc())
        return query.first()

    def resolve_test(self, info):
        return "test"


class CreateBooks(graphene.Mutation):
    id = graphene.String()
    name = graphene.String()

    class Arguments:
        id = graphene.String()
        name = graphene.String()

    def mutate(self, info, id, name):
        book = Book(id=id, name=name)
        session.add(book)
        session.commit()

        return CreateBooks(
            id=book.id,
            name=book.name,
        )


class CreatePapers(graphene.Mutation):
    id = graphene.String()
    update_time = graphene.String()
    paper_name= graphene.String()

    class Arguments:
        id = graphene.String()
        update_time = graphene.String()
        paper_name = graphene.String()

    def mutate(self, info, id, update_time, paper_name):
        paper = Paper(id=id, paper_name=paper_name, update_time=update_time)
        session.add(paper)
        session.commit()

        return CreatePapers(
            id=paper.id,
            paper_name=paper.paper_name,
            update_time=paper.update_time,
        )


class Mutation(graphene.ObjectType):
    create_books = CreateBooks.Field()
    create_papers = CreatePapers.Field()


schema = \
    graphene.Schema(query=Query, mutation=Mutation)
