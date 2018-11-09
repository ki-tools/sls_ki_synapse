import graphene


class Rally(graphene.ObjectType):
    synId = graphene.String()
    number = graphene.Int()
    title = graphene.String()
    rallyTeamId = graphene.Int()

    @staticmethod
    def from_project(project):
        """
        Converts a project to a Rally.
        """
        return Rally(
            synId=project.id,
            number=project.annotations.rally[0],
            title=project.name,
            rallyTeamId=int(project.annotations.rallyTeam[0])
        )
