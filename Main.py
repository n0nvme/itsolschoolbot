import vk
import requests
import TasksDB


def get_messages(server, key, ts):
    return requests.get('https://' + str(server) + '?act=a_check&key=' + str(key)+ '&ts=' + str(ts) + '&wait=25&mode=2&version=2').json()




# initialization, getting longPoll data
problems = TasksDB.TasksDB()
session = vk.Session(access_token='3c67da94695417172da8e3c690cab78a61344d4fabaad75a186c20bc17ea8ec744b3cae5264c7eb8b9b65')
api = vk.API(session)
longPoll = api.messages.getLongPollServer()
longPoll_server = longPoll['server']
longPoll_key = longPoll['key']
longPoll_ts = longPoll['ts']
print(longPoll)

message_states = {}
workers = [161911947]
workers_answers = {}

# main loop
while True:

    # get messages
    messages = get_messages(longPoll_server, longPoll_key, longPoll_ts)
    longPoll_ts = messages['ts']

    # answer
    if len(messages['updates']) != 0:
        if messages['updates'][0][0] == 7: #new message
            message = messages['updates'][1][-2]
            print(message, end=' ')
            message_sender = messages['updates'][0][1]
            print(message_sender)

            # working with student
            if message_sender not in workers:
                if message_states.setdefault(message_sender) == None:
                    message_states[message_sender] = 1
                    api.messages.send(user_id=str(message_sender), message='Привет, опиши свою проблему.')

                elif message_states[message_sender] == 1:
                    api.messages.send(user_id=str(message_sender), message='Где произошла проблема?')
                    message_states[message_sender] = 2
                    problem = message
                elif message_states[message_sender] == 2:
                    api.messages.send(user_id=str(message_sender), message='В скором времени проблема будет устранена.')
                    location = message
                    problems.add_task(problem, location) # Write task to DB
                    message_states[message_sender] = None
                    for i in workers:
                        message_states[i] = None
                        mess = 'Появилась новая проблема\n' + problem + '\n' + location
                        api.messages.send(user_id=str(i), message=mess)
                else: api.messages.send(user_id=str(message_sender), message='техническая ошибка')
            # chat with worker
            else:
                workers_answers[message_sender] = message

                # Return to main message
                if message_states.setdefault(message_sender) is None:
                    message_states[message_sender] = 1
                    mess = 'Выберите действие:\n1. Посмотреть список доступных задач\n2. Показать список выполняемых вами задач'
                    api.messages.send(user_id=message_sender, message=mess)

                # Choice after main message
                elif message_states.setdefault(message_sender) == 1:

                    # Show free tasks
                    if workers_answers[message_sender] == '1':
                        message_states[message_sender] = 2
                        mess = problems.get_all_free_tasks() + 'Чтобы начать выполнять задачу укажите ее номер'
                        api.messages.send(user_id=message_sender, message=mess)

                    # Show tasks in work
                    elif workers_answers[message_sender] == '2':
                        message_states[message_sender] = 3
                        mess = 'На данный момент вы устраняете следующие проблемы:\n' + problems.get_workers_task(message_sender) + 'Чтобы изменить статус задачи укажите ее номер, чтобы выйти отправьте 0'
                        api.messages.send(user_id=message_sender, message=mess)

                    else:
                        message_states[message_sender] = None
                        api.messages.send(user_id=message_sender, message='Неизвестный формат сообщения')

                # Choice after new tasks
                elif message_states.setdefault(message_sender) == 2:
                    message_states[message_sender] = None
                    mess = 'Задача появится в списке выполняемых'
                    api.messages.send(user_id=message_sender, message=mess)

                # Show choice of tasks in work
                elif message_states.setdefault(message_sender) == 3:
                    message_states[message_sender] = 4
                    mess = 'На данный момент вы устраняете следующие проблемы' + problems.get_workers_task(message_sender)
                    api.messages.send(user_id=message_sender, message=mess)

                # Choice of tasks in work
                elif message_states.setdefault(message_sender) == 4:
                    if workers_answers[message_sender] == '0':
                        message_states[message_sender] = 1
                        mess = 'Выберите действие:\n1. Посмотреть список доступных задач\n2. Показать список выполняемых вами задач'
                        api.messages.send(user_id=message_sender, message=mess)
                    elif workers_answers[message_sender] != '1':
                        message_states[message_sender] = 5
                        mess = 'Что вы хотите сделать?\n1. Отметить задачу как выполненную\n2. Отказаться от выполнения задачи'

                # Last choice
                elif message_states.setdefault(message_sender) == 5:
                    message_states[message_sender] = None
                    if workers_answers[message_sender] == '1':
                        mess = 'Задача отмечена как выполненная'
                        api.messages.send(user_id=message_sender, message=mess)
                    elif workers_answers[message_sender] == '2':
                        mess = 'Вы отказались от этой задачи'
                        api.messages.send(user_id=message_sender, message=mess)

    else: continue
