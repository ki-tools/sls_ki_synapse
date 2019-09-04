import graphene


class WikiDataInput(graphene.InputObjectType):
    """
    Input class for 'wiki' data.
    """
    title = graphene.String(required=True)
    markdown = graphene.String()
