import graphene


class AnnotationDataInput(graphene.InputObjectType):
    """
    Input class for 'annotations' data.
    """
    key = graphene.String(required=True)
    value = graphene.String(required=True)
