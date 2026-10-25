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
        Item={'todo_id': str(uuid.uuid4()), 'title': title, 'status': 'Pending'}
    )
  return redirect(url_for('index'))


@app.route('/delete/<todo_id>')
def delete_todo(todo_id):
    # Deletes the item from your DynamoDB 'Todos' table
    table.delete_item(
        Key={
            'id': todo_id  # (Change 'id' to whatever your primary partition key name is in DynamoDB, e.g., 'todo_id')
        }
    )
    return redirect(url_for('index'))

@app.route('/complete/<todo_id>')
def complete_todo(todo_id):
    # Optional: Update status in DynamoDB if you track completion
    return redirect(url_for('index'))

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)
