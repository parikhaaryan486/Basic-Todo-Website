import os
import uuid
import boto3
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__, template_folder='Website')

# Initialize DynamoDB client (uses IAM role attached to EC2)
dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
table_name = os.environ.get('DYNAMODB_TABLE', 'Todos')
table = dynamodb.Table(table_name)


@app.route('/')
def index():
    # Scan or query items from DynamoDB
    response = table.scan()
    todos = response.get('Items', [])
    return render_template('index.html', todos=todos)


@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    if title:
        table.put_item(
            Item={
                'todo_id': str(uuid.uuid4()), 
                'title': title, 
                'completed': False  # Matches the toggle check in your HTML
            }
        )
    return redirect(url_for('index'))


@app.route('/update/<todo_id>', methods=['POST'])
def update_todo(todo_id):
    # Fetch current task status to toggle it
    response = table.get_item(Key={'todo_id': todo_id})
    if 'Item' in response:
        current_status = response['Item'].get('completed', False)
        table.update_item(
            Key={'todo_id': todo_id},
            UpdateExpression='SET completed = :val',
            ExpressionAttributeValues={':val': not current_status}
        )
    return redirect(url_for('index'))


@app.route('/delete/<todo_id>', methods=['POST'])
def delete_todo(todo_id):
    # Deletes the item using the correct 'todo_id' primary key
    table.delete_item(
        Key={
            'todo_id': todo_id
        }
    )
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
