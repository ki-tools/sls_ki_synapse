import graphene


class Rally(graphene.ObjectType):
    """
    Defines the Rally type.
    """
    synId = graphene.String()
    number = graphene.Int()
    title = graphene.String()
    rallyTeamId = graphene.Int()

    @staticmethod
    def from_project(project):
        """
        Converts a Project to a Rally.
        """
        return Rally(
            synId=project.id,
            number=project.annotations.rally[0],
            title=project.name,
            rallyTeamId=int(project.annotations.rallyTeam[0])
        )
