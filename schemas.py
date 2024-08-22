import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from models import Product as ProductModel, db

class Product(SQLAlchemyObjectType):
    class Meta:
        model = ProductModel

class Query(graphene.ObjectType):
    products = graphene.List(Product)
    search_products = graphene.List(Product, id=graphene.Int(), name=graphene.String(), category=graphene.Int(), price=graphene.Float())

    def resolve_products(self, info):
        return db.session.execute(db.select(ProductModel)).scalars()
    
    def resolve_search_products(self, info, id=None, name=None, category=None, price=None):
        query = db.select(ProductModel)
        if id:
            query = query.where(ProductModel.id == id)
        if name:
            query = query.where(ProductModel.name.ilike(f'%{name}%'))
        if category:
            query = query.where(ProductModel.category.ilike(f'%category%') )
        if price:
            query = query.where(ProductModel.price == price)
        results = db. session.execute(query).scalars().all()
        return results

    
class AddProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        category = graphene.String(required=True)
        quantity = graphene.Int(required=True)
        price = graphene.Int(required=True)
    
    product = graphene.Field(Product)

    def mutate(self, info, name, category, quantity, price):
        product = ProductModel(name=name, category=category, quantity=quantity, price=price)
        db.session.add(product)
        db.session.commit()
        db.session.refresh(product)

        return AddProduct(product=product)

class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=False)
        category = graphene.String(required=False)
        quantity = graphene.Int(required=False)
        price = graphene.Float(required=False)

    product = graphene.Field(Product)

    def mutate(self, info, id, name=None, category=None, quantity=None, price=None):
        product = db.session.get(ProductModel, id)
        if not product:
            return None
        if name:
            product.name = name
        if category:
            product.category = category
        if quantity:
            product.quantity = quantity
        if price:
            product.price = price
        
        db.session.add(product)
        db.session.commit()
        return UpdateProduct(product=product)

class DeleteProduct(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    product = graphene.Field(Product)

    def mutate(self, info, id):
        product = db.session.get(ProductModel, id)
        if not product:
            return None
        db.session.delete(product)
        db.session.commit()
        return DeleteProduct(product=product)

class Mutation(graphene.ObjectType):
    create_product = AddProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()