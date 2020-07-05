import os
import urllib.request
import urllib.error

import boto3
import json
from PIL import Image

import rng


IMAGE_URL = 'http://collface.deptcpanel.princeton.edu/img/{}'


def _main():
    os.environ['AWS_PROFILE'] = 'tongue'

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    student_table = dynamodb.Table('dynamo-tongue-student-prod')

    s3 = boto3.resource('s3', region_name='us-east-1')
    image_bucket = s3.Bucket('tongue-image')

    with open('princeton_all.json', 'r') as data:
        students = json.loads(data.read())['data']
        student_count = len(students)

        with student_table.batch_writer() as batch:
            for i, student in enumerate(students):
                if i < 900:
                    continue
                # Get student information in a friendly form.
                name = student['name']
                fname = name.split(' ')[0]
                lname = name.split(' ')[-1]
                year = student['class_yr']
                possible_ids = student['email'].split('@')
                assert len(possible_ids) == 2
                net_id = possible_ids[0]
                study = student['acad_plan_descr'] or 'Undeclared'
                # Collface hasn't yet changed Woodrow Wilson, so we're going to
                # do the right thing.
                if "Woodrow Wilson".upper() in study.upper():
                    study = "Public and International Affairs"
                degree = 'BSE' if 'BSE' in student['program'] else 'AB'
                # Collface has fixed Wilson College, however.
                college = student['college'].lower().capitalize()
                if college == 'Rkefeller':
                    college = 'Rocky'
                if college == 'First':
                    college = 'First College'
                image = student['img']
                image_url = IMAGE_URL.format(image)

                # Download the image.
                try:
                    urllib.request.urlretrieve(image_url, 'temp_image.jpg')
                except urllib.error.HTTPError as e:
                    print('When considering', image_url)
                    print('For', name)
                    print('error:', e)
                photo = Image.open('temp_image.jpg')
                photo_raw = Image.new(photo.mode, photo.size)
                photo_raw.putdata(list(photo.getdata()))
                try:
                    photo_raw.save('image_large.jpg')
                    photo_raw.thumbnail((64, 64), Image.ANTIALIAS)
                    photo_raw.save('image_small.jpg')
                except Exception as e:
                    print('When considering', image_url)
                    print('For', name)
                    print('error:', e)
                    print('trying again...')
                    photo_raw = photo_raw.convert("RGB")
                    photo_raw.save('image_large.jpg')
                    photo_raw.thumbnail((64, 64), Image.ANTIALIAS)
                    photo_raw.save('image_small.jpg')

                # Create a new resource ID for the image.
                image_id = rng.id(24) + '.jpg'

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
                        'image': image_id
                    }
                )

                # Upload the image to s3.
                image_bucket.upload_file('image_large.jpg',
                                         'prod/large/{}'.format(image_id))
                image_bucket.upload_file('image_small.jpg',
                                         'prod/small/{}'.format(image_id))

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
