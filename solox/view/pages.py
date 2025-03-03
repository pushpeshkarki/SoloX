import json
import os
from flask import Blueprint
from flask import render_template
from flask import request
from logzero import logger
from solox.public.common import Devices,File,Method

page = Blueprint("page", __name__)
d = Devices()
m = Method()
f = File()

@page.app_errorhandler(404)
def page_404(e):
    settings = m._settings(request)
    return render_template('404.html', **locals()), 404

@page.app_errorhandler(500)
def page_500(e):
    settings = m._settings(request)
    return render_template('500.html', **locals()), 500

@page.route('/')
def index():
    platform = request.args.get('platform')
    lan = request.args.get('lan')
    settings = m._settings(request)
    return render_template('index.html', **locals())

@page.route('/pk')
def pk():
    lan = request.args.get('lan')
    model = request.args.get('model')
    settings = m._settings(request)
    return render_template('pk.html', **locals())

@page.route('/report')
def report():
    lan = request.args.get('lan')
    settings = m._settings(request)
    report_dir = os.path.join(os.getcwd(), 'report')
    try:
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        dirs = os.listdir(report_dir)
        dir_list = reversed(sorted(dirs, key=lambda x: os.path.getmtime(os.path.join(report_dir, x))))
        apm_data = []
        for dir in dir_list:
            if dir.split(".")[-1] not in ['log', 'json', 'mkv']:
                try:
                    with open(os.path.join(report_dir, dir, 'result.json'), 'r') as fpath:
                        json_data = json.loads(fpath.read())
                        dict_data = {
                            'scene': dir,
                            'app': json_data.get('app'),
                            'platform': json_data.get('platform'),
                            'model': json_data.get('model'),
                            'devices': json_data.get('devices'),
                            'ctime': json_data.get('ctime'),
                            'video': json_data.get('video', 0)
                        }
                        # Validate required fields
                        if not all(dict_data[key] for key in ['app', 'platform', 'model', 'devices', 'ctime']):
                            logger.warning(f"Missing required fields in report file {dir}")
                            continue
                        apm_data.append(dict_data)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    logger.error(f"Error reading report file {dir}: {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error processing report file {dir}: {str(e)}")
                    logger.exception(e)
                    continue
    except Exception as e:
        logger.error(f"Error accessing report directory: {str(e)}")
        logger.exception(e)
        apm_data = []
    apm_data_len = len(apm_data)
    return render_template('report.html', **locals())

@page.route('/analysis', methods=['post', 'get'])
def analysis():
    lan = request.args.get('lan')
    scene = request.args.get('scene')
    app = request.args.get('app')
    platform = request.args.get('platform')
    settings = m._settings(request)
    report_dir = os.path.join(os.getcwd(), 'report')
    dirs = os.listdir(report_dir)
    filter_dir = f.filter_secen(scene)
    apm_data = {}
    for dir in dirs:
        if dir == scene:
            try:
                if platform == 'Android':
                    apm_data = f._setAndroidPerfs(scene)
                    disk = f.analysisDisk(scene)
                    initial_disk  = disk[0]
                    current_disk  = disk[1]
                    sum_init_disk = disk[2]
                    sum_current_disk = disk[3]
                else:
                    apm_data = f._setiOSPerfs(scene)
            except ZeroDivisionError:
                pass    
            except Exception as e:
                logger.exception(e)
            finally:
                break
    return render_template('analysis.html', **locals())

@page.route('/pk_analysis', methods=['post', 'get'])
def analysis_pk():
    """Analyze performance comparison data"""
    lan = request.args.get('lan')
    scene = request.args.get('scene')
    app = request.args.get('app')
    model = request.args.get('model')
    settings = m._settings(request)
    
    try:
        report_dir = os.path.join(os.getcwd(), 'report')
        if not os.path.exists(report_dir):
            raise FileNotFoundError("Report directory does not exist")
            
        dirs = os.listdir(report_dir)
        apm_data = {}
        
        if scene in dirs:
            try:
                apm_data = f._setpkPerfs(scene)
            except Exception as e:
                logger.error(f"Error processing performance data for scene {scene}: {str(e)}")
                logger.exception(e)
    except Exception as e:
        logger.error(f"Error accessing report data: {str(e)}")
        logger.exception(e)
        
    return render_template('analysis_pk.html', **locals())

@page.route('/compare_analysis', methods=['post', 'get'])
def analysis_compare():
    """Compare performance analysis between two scenes"""
    platform = request.args.get('platform')
    lan = request.args.get('lan')
    scene1 = request.args.get('scene1')
    scene2 = request.args.get('scene2')
    app = request.args.get('app')
    settings = m._settings(request)
    
    try:
        if not all([platform, scene1, scene2]):
            raise ValueError("Missing required parameters: platform, scene1, or scene2")
            
        if platform not in ['Android', 'iOS']:
            raise ValueError(f"Unsupported platform: {platform}")
            
        try:
            if platform == 'Android':
                apm_data1 = f._setAndroidPerfs(scene1)
                apm_data2 = f._setAndroidPerfs(scene2)
            else:  # iOS
                apm_data1 = f._setiOSPerfs(scene1)
                apm_data2 = f._setiOSPerfs(scene2)
        except ZeroDivisionError as e:
            logger.warning(f"Division by zero error in performance data: {str(e)}")
            apm_data1 = None
            apm_data2 = None
        except Exception as e:
            logger.error(f"Error processing performance data: {str(e)}")
            logger.exception(e)
            apm_data1 = None
            apm_data2 = None
    except Exception as e:
        logger.error(f"Error in comparison analysis: {str(e)}")
        logger.exception(e)
        apm_data1 = None
        apm_data2 = None
        
    return render_template('analysis_compare.html', **locals())
