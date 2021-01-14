#!/usr/bin/env python3
"""Populate the database with information from TigerFace.

Ideally this would be run automatically from a lambda every two weeks or so,
but the AWS VPN is not in the Princeton network so we can't access the API.
"""

import base64
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile

import boto3
import json
from PIL import Image


IMAGE_DIRECTORY_LARGE = 'prod/large'
IMAGE_DIRECTORY_SMALL = 'prod/small'


def _main():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    student_table = dynamodb.Table(os.environ['TX_DYNAMODB_STUDENT_TABLE'])

    # Get data from the Tiger Face API. ----------------------------------------

    # Right now, we use a downloaded version of the output of the TigerFace
    # API because the QA API endpoint is protected and must be accessed
    # through a VPN outside of Princeton. Since logging into the VPN is not
    # easily done through a script, we'll just use a local JSON file until
    # we can use the production endpoint which does not require a VPN.
    students = None
    try:
        with open('{}/tiger_face_out.json'.format(os.environ['ROOT']), 'r') as data:
            students = json.loads(data.read())
        print('Loaded {} students from the API.'.format(len(students)))
    except:
        print('Error accessing the API.', file=sys.stderr)
        exit(1)
    assert students

    student_no_name_count = 0
    student_no_photo_count = 0

    # Handle each student's data upload. We could divide the data into multiple
    # processes to do the upload, but this is unnecessary, as the entire thing
    # takes less than a minute.
    with student_table.batch_writer() as batch, tempfile.TemporaryDirectory() as temporary_directory:
        os.makedirs('{}/{}'.format(temporary_directory, IMAGE_DIRECTORY_LARGE))
        os.makedirs('{}/{}'.format(temporary_directory, IMAGE_DIRECTORY_SMALL))
        for i, student in enumerate(students):
            # Get student information in a friendly form.

            # Student name.
            name = student['name']
            if not name:
                # Seems like TigerFace has some test students that don't have
                # a name. We'll have to skip these.
                student_no_name_count += 1
                continue
            fname = name.split(' ')[0]
            lname = name.split(' ')[-1]

            # Student year and academic information.
            year = student['class_year']
            assert year in ['2021', '2022', '2023', '2024']
            study = student['plan_description'] or 'Undeclared'
            degree = student['acad_prog']

            # Student college.
            college = student['res_college'] or 'No res college'

            # If the email address has only a single @ sign, we assume
            # the token before it is the student's netid.
            possible_ids = student['email'].split('@')
            assert len(possible_ids) == 2
            net_id = possible_ids[0]

            # Student photo.
            photo_bytes_encoded = student['photo']
            if photo_bytes_encoded:
                # Decode the image.
                photo_bytes = base64.b64decode(photo_bytes_encoded)

                with Image.open(io.BytesIO(photo_bytes)) as photo:
                    # Convert the photo into large and small thumbnails
                    # to use on the website. Save them with a hash-based
                    # filename so we can sync to S3 without uploading data
                    # that's already there.

                    # Large thumbnail.
                    photo.thumbnail((276, 276), Image.ANTIALIAS)
                    photo_hash = hashlib.md5(photo.tobytes()).hexdigest()
                    photo_name_large = ('{}/{}.webp'.format(
                        IMAGE_DIRECTORY_LARGE,
                        photo_hash
                    ))
                    photo.save('{}/{}'.format(
                        temporary_directory,
                        photo_name_large
                    ))

                    # Small thumbnail.
                    photo.thumbnail((128, 128), Image.ANTIALIAS)
                    photo_hash = hashlib.md5(photo.tobytes()).hexdigest()
                    photo_name_small = ('{}/{}.webp'.format(
                        IMAGE_DIRECTORY_SMALL,
                        photo_hash
                    ))
                    photo.save('{}/{}'.format(
                        temporary_directory,
                        photo_name_small
                    ))
            else:
                # TigerFace has no photo for anyone in class years 2021 or 2024.
                # We'll still upload these students.
                student_no_photo_count += 1
                photo_name_large = '{}/{}.webp'.format(
                    IMAGE_DIRECTORY_LARGE,
                    'default'
                )
                photo_name_small = '{}/{}.webp'.format(
                    IMAGE_DIRECTORY_SMALL,
                    'default'
                )
            
            # Put the student data into DynamoDB.
            # Attributes that start with '_' will be used as indices.
            batch.put_item(
                Item={
                    '_netid': net_id.upper(),

                    '_fname': fname.upper(),
                    '_lname': lname.upper(),
                    '_study': study.upper(),
                    '_college': college.upper(),

                    'netid': net_id,
                    'name': name,
                    'year': year,
                    'study': study,
                    'degree': degree,
                    'college': college,
                    'photo_large': photo_name_large,
                    'photo_small': photo_name_small,
                }
            )

            # Print progress.
            if i != 0 and i % 300 == 0:
                print('{}%'.format(int(100 * (i / len(students)))))
        
        # Sync the photos to S3.
        subprocess.run([
            'aws', 's3', 'sync',
            temporary_directory + '/prod',
            's3://{}/prod'.format(os.environ['TX_S3_IMAGE_BUCKET']),
            # Remove files from remote if they are not needed anymore.
            '--delete',
            # Do not update the files on remote just because their timestamp
            # is newer on local. Instead base off filename and size.
            '--size-only'
        ])

        # Copy the images to the static directory so we can serve them
        # locally. When we have a populate dev script, we'll do this without
        # syncing to S3 above.
        shutil.copytree(
            temporary_directory + '/prod',
            "{}/source/static/prod".format(os.environ['ROOT'])
        )

    print(' skipped {} students with no name'.format(student_no_name_count))
    print(' kept {} students with no photo'.format(student_no_photo_count))


if __name__ == '__main__':
    _main()
