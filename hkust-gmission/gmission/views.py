__author__ = 'CHEN Zhao'


import time
import admin
import blueprints

from flask_app import app, cache
import rest
from flask import render_template, request, redirect, jsonify, g
from models import *
from controllers import task_controller

import json

app.register_blueprint(blueprints.user_bp,      url_prefix='/user')
app.register_blueprint(blueprints.image_bp,     url_prefix='/image')
app.register_blueprint(blueprints.video_bp,     url_prefix='/video')
app.register_blueprint(blueprints.audio_bp,     url_prefix='/audio')
# flask_app.register_blueprint(blueprints._bp,     url_prefix='/portal')
app.register_blueprint(blueprints.zzy_map_bp,   url_prefix='/mapping')
app.register_blueprint(blueprints.shortcut_bp,  url_prefix='/shortcut')

rest.ReSTManager.init_rest(app)
# admin.init_admin()


def profile_log(*l):
    app.profiling_logger.debug(l)


@app.route('/')
def index():
    return render_template('index.html', config=app.config)

@app.route('/rating')
def rating():
    return render_template('rating.html')

@app.route('/assignWorkers')
def assign_workers():
    task_controller.assign_temporal_task_to_workers()
    return "assignWorkers OK"

@app.route('/test')
def test():
    # for u in User.query.filter(User.id==49):
    #     return str(task_controller.query_online_users())
    # task = Task.query.filter(Task.id == '435').limit(1).all()
    # task_controller.calibrate_temporal_task_worker_velocity(task[0])
    # return str(task_controller.write_available_worker_profiles_to_file(1))
    # task_controller.calibrate_worker_profile()
    # task_controller.export_temporal_task_results([424], 'test')
    # task_controller.test()
    # task_controller.calibrate_worker_profile()
    return "test OK"


@app.route('/prepareTemporalTaskAnswers')
def prepareTemporalTaskAnswers():
    task_controller.extract_temporal_task_answers_to_table()
    return "prepare OK"

@app.route('/getAnswerMessage', methods=['POST'])
def getTemporalAnswerById():
    answer_id = request.form['answer_id']
    temporal_answer = TemporalTaskAnswer.query.get(answer_id)
    if temporal_answer is not None:
        task = Task.query.get(temporal_answer.task_id)

        return jsonify(current_anwer_id=temporal_answer.id,
                       brief=temporal_answer.brief,
                       location_content=task.location.name,
                       task_lat=temporal_answer.task_latitude,
                       task_lon=temporal_answer.task_longitude,
                       worker_lat=temporal_answer.worker_profile.latitude,
                       worker_lon=temporal_answer.worker_profile.longitude,
                       pic_name=temporal_answer.attachment.value
                       )


@app.route('/rateTemporalAnswer', methods=['POST'])
def rateTemporalAnswer():
    print 'here'
    answer_id = request.form['answer_id']
    worker_email = request.form['email_address']
    value = request.form['value']
    rater = User.query.filter(User.email==worker_email).all()
    if len(rater) != 0:
        rater_id = rater[0].id
    else:
        rater_id = 1

    temporal_answer_rating = TemporalTaskAnswerRating(answer_id=answer_id,
                                                      rater_id=rater_id,
                                                      value=value)
    next_temporal_answer = TemporalTaskAnswer.query.filter(TemporalTaskAnswer.id > answer_id).limit(1).all()
    if len(next_temporal_answer) == 0:
        next_answer_id = -1
    else:
        next_answer_id = next_temporal_answer[0].id

    db.session.add(temporal_answer_rating)
    db.session.commit()

    return jsonify(next_answer_id=next_answer_id)


@app.route('/cleanTemporalTask')
def cleanTemporalTask():
    # for u in User.query.filter(User.id==49):
    #     return str(task_controller.query_online_users())
    # task = Task.query.filter(Task.id == '435').limit(1).all()
    # task_controller.calibrate_temporal_task_worker_velocity(task[0])
    # return str(task_controller.write_available_worker_profiles_to_file(1))
    # task_controller.calibrate_worker_profile()
    task_controller.clean_temporal_tasks_and_messages()
    # task_controller.test()
    return "test OK"


@app.route('/export')
def export():
    # task_controller.export_temporal_task_results(range(424,429), 'random_1min')  #redo
    # task_controller.export_temporal_task_results(range(429,434), 'random_2min')
    # task_controller.export_temporal_task_results(range(434,439), 'random_3min')
    # task_controller.export_temporal_task_results(range(439,444), 'random_4min')
    # task_controller.export_temporal_task_results(range(541,546), 'greedy_1min')
    # task_controller.export_temporal_task_results(range(546,551), 'greedy_2min')
    # task_controller.export_temporal_task_results(range(551,556), 'greedy_3min')
    # task_controller.export_temporal_task_results(range(556,566), 'greedy_4min')

    task_controller.export_temporal_task_results(range(623,628), 'sampling_1min')
    task_controller.export_temporal_task_results(range(707,712), 'sampling_2min')
    task_controller.export_temporal_task_results(range(722,727), 'sampling_3min')
    task_controller.export_temporal_task_results(range(616,621), 'sampling_4min')

    task_controller.export_temporal_task_results(range(732,737), 'dv_1min')
    task_controller.export_temporal_task_results(range(737,742), 'dv_2min')
    task_controller.export_temporal_task_results(range(742,747), 'dv_3min')
    task_controller.export_temporal_task_results(range(747,752), 'dv_4min')

    task_controller.export_temporal_task_results(range(752,757), 'ground_1min')
    task_controller.export_temporal_task_results(range(757,762), 'ground_3min')
    # task_controller.export_temporal_task_results(range(722,727), 'sampling_3min')
    # task_controller.export_temporal_task_results(range(616,621), 'sampling_4min')
    return "export OK"


@app.route('/marauders-map')
def marauders_map():
    users = User.query.all()

    user_traces = {}
    # for u in User.query.all()[:50]:
    for u in User.query.filter(User.id==36):
        traces = PositionTrace.query.filter_by(user=u).all()
        user_traces[u.id] = [(t.longitude, t.latitude) for t in traces]

    return render_template('marauders_map.html', users=users, user_traces=json.dumps(user_traces))



@cache.cached(timeout=3600, key_prefix='crabwords')
def load_crabwords():
    return [w.word for w in SensitiveWord.query.all()]


def is_cached_url(url):
    return url.endswith('/rest/location')


@app.before_request
def before_request():
    g.request_start_time = time.time()  # time.time is precise enough

    # if is_cached_url(request.url):
    #     cached_response = cache.get(request.url)
    #     if cached_response:
    #         cached_response.simple_url_cached = True
    #         return cached_response

    g.crabwords = [] #load_crabwords()

    profile_log(request.path, 'crab', time.time()-g.request_start_time)
    # print "[Before request:%s %s, %s]" % (request.method, request.url, request.json)


@app.after_request
def after_request(response):
    # resp_brief = response.data[:200] if 'json' in response.mimetype else ''
    # print "[After request:%s %s, %d, %s, %s]" % \
    #       (request.method, request.url, response.status_code, response.mimetype, resp_brief)
    # if not getattr(response, 'simple_url_cached', False):
    #     cache.set(request.url, response)
    return response


@app.teardown_request
def teardown_request(l):
    profile_log(request.path, time.time()-g.request_start_time)


@app.route('/matlab/<directory>')
def matlab(directory):
    return directory



#409 Conflict: the best HTTP code I can find
@app.errorhandler(409)
def conflict(e):
    print 'conflict!'
    obj = e.conflict_obj
    obj_dict = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    return jsonify(**obj_dict)
    # print e.get_single_url
    # return redirect(e.get_single_url, code=303)  # something wrong with redirect

