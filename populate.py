import os

import boto3
import json


IMAGE_URL = 'http://collface.deptcpanel.princeton.edu/img/{}'


def _main():
    os.environ['AWS_PROFILE'] = 'tongue'

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    student_table = dynamodb.Table('dynamo-tongue-student-prod')

    with open('all_princeton_new.json', 'r') as data:
        students = json.loads(data.read())['data']
        student_count = len(students)

        with student_table.batch_writer() as batch:
            for i, student in enumerate(students):
                # Get student information in a friendly form.
                name = student['name']
                fname = name.split(' ')[0]
                lname = name.split(' ')[-1]
                year = student['class_yr']
                possible_ids = student['email'].split('@')
                assert len(possible_ids) == 2
                net_id = possible_ids[0]
                study = student['acad_plan_descr'] or 'Undeclared'
                degree = 'BSE' if 'BSE' in student['program'] else 'AB'
                college = student['college'].lower().capitalize()
                if college == 'Rkefeller':
                    college = 'Rocky'
                if college == 'First':
                    college = 'First College'
                image = student['img']
                image_url = IMAGE_URL.format(image)
                # Right now we aren't hosting the images ourselves,
                # just serving them from collface.

                batch.put_item(
                    Item={
                        '_netId': net_id.upper(),
                        '_name': name.upper(),
                        '_fname': fname.upper(),
                        '_lname': lname.upper(),

                        'netId': net_id,
                        'name': name,
                        'year': year,
                        'study': study,
                        'degree': degree,
                        'college': college,
                        'image': image
                    }
                )

                if i != 0 and i % 300 == 0:
                    print(100 * (i / student_count), '%')


    exit(0)

    
    # Get the student's information.
    response = student_table.get_item(
        Key={
            'netId': net_id
        }
    )


if __name__ == '__main__':
    _main()
