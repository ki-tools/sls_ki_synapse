# Copyright 2018-present, Bill & Melinda Gates Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import graphene
import os
import json
import requests
import tempfile
from time import gmtime, strftime
import boto3
from core import ParamStore
from ..types import SlideDeck
from pptx import Presentation


class CreateSlideDeck(graphene.Mutation):
    """
    Mutation for creating a SlideDeck.
    """
    ok = graphene.Boolean()
    slide_deck = graphene.Field(lambda: SlideDeck)

    class Arguments:
        title = graphene.String(required=True)
        presenter = graphene.String(required=True)
        sprint_id = graphene.String(required=True)
        participants = graphene.List(graphene.String, required=True)
        end_date = graphene.String(required=True)
        sprint_questions = graphene.List(graphene.String, required=True)
        background = graphene.String(required=True)
        problem_statement = graphene.String(required=True)
        motivation = graphene.String(required=True)
        deliverables = graphene.List(graphene.String, required=True)
        key_findings = graphene.List(graphene.String, required=True)
        next_steps = graphene.List(graphene.String, required=True)
        value = graphene.String(required=True)

    def mutate(self,
               info,
               title,
               presenter,
               sprint_id,
               participants,
               end_date,
               sprint_questions,
               background,
               problem_statement,
               motivation,
               deliverables,
               key_findings,
               next_steps,
               value):

        pptx_path = 'assets/template_ki_empty.pptx'
        presentation = Presentation(pptx_path)

        SLD_TITLE = 0
        SLD_HEAD_COPY = 1
        SLD_HEAD_BULLETS = 2
        # SLD_HEAD_SUBHEAD_COPY = 3
        # SLD_HEAD_ONLY = 7
        SLD_INSTRUCTIONS = 9

        title_layout = presentation.slide_layouts[SLD_TITLE]
        plain_layout = presentation.slide_layouts[SLD_HEAD_COPY]
        bullet_layout = presentation.slide_layouts[SLD_HEAD_BULLETS]

        # deliverables

        slide = presentation.slides.add_slide(bullet_layout)
        shapes = slide.shapes
        title_shape = shapes.title
        body_shape = shapes.placeholders[16]
        title_shape.text = 'Deliverables'
        tf = body_shape.text_frame
        for item in deliverables:
            p = tf.add_paragraph()
            p.text = item
            p.level = 1

        CreateSlideDeck.move_to_front(presentation)

        # questions

        slide = presentation.slides.add_slide(bullet_layout)
        shapes = slide.shapes
        title_shape = shapes.title
        body_shape = shapes.placeholders[16]
        title_shape.text = 'Sprint Questions'
        tf = body_shape.text_frame
        for item in sprint_questions:
            p = tf.add_paragraph()
            p.text = item
            p.level = 1

        CreateSlideDeck.move_to_front(presentation)

        # problem statement

        slide = presentation.slides.add_slide(plain_layout)
        slide.placeholders[0].text = "Problem Statement"
        slide.placeholders[16].text = problem_statement

        CreateSlideDeck.move_to_front(presentation)

        # motivation

        slide = presentation.slides.add_slide(plain_layout)
        slide.placeholders[0].text = "Motivation"
        slide.placeholders[16].text = motivation

        CreateSlideDeck.move_to_front(presentation)

        # background

        slide = presentation.slides.add_slide(plain_layout)
        slide.placeholders[0].text = "Background"
        slide.placeholders[16].text = background

        CreateSlideDeck.move_to_front(presentation)

        # title slide

        slide = presentation.slides.add_slide(title_layout)
        slide.placeholders[0].text = 'Rally {0}: {1}'.format(sprint_id, title)
        slide.placeholders[15].text = 'Completed {0}'.format(end_date)
        slide.placeholders[17].text = 'Presented by {0} on behalf of rally participants {1}'.format(
            presenter, ', '.join(participants))

        CreateSlideDeck.move_to_front(presentation)

        # data/methods/results are already part of the deck

        # key findings

        slide = presentation.slides.add_slide(bullet_layout)
        shapes = slide.shapes
        title_shape = shapes.title
        body_shape = shapes.placeholders[16]
        title_shape.text = 'Key Findings'
        tf = body_shape.text_frame
        for item in key_findings:
            p = tf.add_paragraph()
            p.text = item
            p.level = 1

        # value

        slide = presentation.slides.add_slide(plain_layout)
        slide.placeholders[0].text = "Value"
        slide.placeholders[16].text = value

        # next steps

        slide = presentation.slides.add_slide(bullet_layout)
        shapes = slide.shapes
        title_shape = shapes.title
        body_shape = shapes.placeholders[16]
        title_shape.text = 'Next Steps'
        tf = body_shape.text_frame
        items = next_steps
        for item in items:
            p = tf.add_paragraph()
            p.text = item
            p.level = 1

        # remove INSTRUCTIONS slide before saving

        slides = list(presentation.slides)
        slides2 = list(presentation.slides._sldIdLst)
        rm_idx = next((i for i in range(len(slides))
                       if slides[i].slide_layout.name == 'INSTRUCTIONS'), None)
        if rm_idx != None:
            presentation.slides._sldIdLst.remove(slides2[rm_idx])

        ppt_file_name = 'rally{0}_{1}.pptx'.format(
            sprint_id, strftime('%Y-%m-%d_%H%M%S', gmtime()))

        ppt_file_full_path = os.path.join(tempfile.gettempdir(), ppt_file_name)

        presentation.save(ppt_file_full_path)

        # Store on S3
        s3 = boto3.resource('s3')

        s3.meta.client.upload_file(
            ppt_file_full_path, ParamStore.SLIDE_DECKS_BUCKET_NAME(), ppt_file_name)

        url = s3.meta.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': ParamStore.SLIDE_DECKS_BUCKET_NAME(),
                    'Key': ppt_file_name},
            ExpiresIn=3600
        )

        if os.path.isfile(ppt_file_full_path):
            os.remove(ppt_file_full_path)

        new_slide_deck = SlideDeck(url=url)

        is_ok = True
        return CreateSlideDeck(slide_deck=new_slide_deck, ok=is_ok)

    @staticmethod
    def move_to_front(presentation):
        last_slide = len(presentation.slides) - 1
        slides = list(presentation.slides._sldIdLst)
        presentation.slides._sldIdLst.remove(slides[last_slide])
        presentation.slides._sldIdLst.insert(0, slides[last_slide])
