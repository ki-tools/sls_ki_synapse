import graphene


class PostDataInput(graphene.InputObjectType):
    """
    Input class for 'posts' data.
    """
    title = graphene.String(required=True)
    messageMarkdown = graphene.String()
