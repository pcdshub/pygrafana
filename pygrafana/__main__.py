import sys
import argparse
import json
from .grafana import fetch_alert, delete_alert_rule, fetch_alert_group, update_alert_rule
from .serialize_alert import ProvisionedAlertRule, AlertGroup, Evaluator
from .create_alert import AlertCreater

fms_happi_database = "fms_test.json"

def create_alert(value, title, folder_name, rule_group, polarity, pv, happi_name):
    ac = AlertCreater()

    ac.create_alert(
        value,
        alert_title=title,
        folder_name=folder_name,
        rule_group=rule_group,
        pv=pv,
        happi_name=happi_name,
        polarity=polarity)

def delete_alert(alert_uid):
    delete_alert_rule(alert_uid)

def update_alert(alert_uid, annotations=None, title=None, pending=None, labels=None, thresh=None):
    alert = fetch_alert(alert_uid)
    alert_rule = ProvisionedAlertRule.parse_raw(alert)

    if annotations is not None:
        alert_rule.annotations = annotations
    elif title is not None:
        alert_rule.title = title 
    elif pending is not None:
        alert_rule.for_ = pending
    elif labels is not None:
        alert_rule.labels = labels
    elif thresh is not None:
        alert_rule.data[1].model.conditions[0]["evaluator"] = Evaluator(params=[thresh, 0])
    else:
        print("No update parameters provided, exit")
        exit()

    update_alert_rule(alert_uid, json.dumps(alert_rule.dict(by_alias=True)))

def get_alert_group(folder_uid, group):
    alert_group = fetch_alert_group(folder_uid, group)
    alert = AlertGroup.parse_obj(alert_group)
    print(alert)

def get_alert(alert_uid):
    alert = fetch_alert(alert_uid)
    print(alert)
    #alert_rule = ProvisionedAlertRule.parse_raw(alert)
    #print(alert_rule)

def SetupArgumentParser():
    parser = argparse.ArgumentParser(
                        prog="pygrafana",
                        description='A CLI for interacting with grafana',
                        epilog='Thank you for using the pygrafana CLI!')
    
    parser.add_argument('-t','--title', dest='title', help='name of alert rule')
    parser.add_argument('-f','--folder', dest='folder_name', help='grafana alert folder name')
    parser.add_argument('-r','--rule_g', dest='rule_group', help='name of alert rule group')
    parser.add_argument('-v','--thresh', dest='thresh_value', help='alert trip point')
    parser.add_argument('-pl','--polarity', dest='polarity', help='alert high or low', choices=["gt", "lt"], default=None)
    parser.add_argument('-pv','--pv', dest='prefix', help='epics PV', default=None)
    parser.add_argument('-hn','--happi_name', dest='happi_name', help='happi database name', default=None)
    parser.add_argument('-an','--annotations', dest='annotations', help="Annotations is a JSON-formatted string (e.g., '{\"description\": \"value1\", \"message\": \"value2\"}')", default=None)
    parser.add_argument('-l','--labels', dest='labels', help="labels is a JSON-formatted string (e.g., '{\"subsystem\": \"fms\", \"key2\": \"value2\"}')", default=None)
    parser.add_argument('-p','--pending', dest='pending', help="Pending time for alert", choices=["2m","5m", "10m", "1h", "2h", "5h", "1d"], default=None)


    parser.add_argument('--get_alert', action='store_true', help='get alert rule')
    parser.add_argument('--get_alert_group', action='store_true', help='get alert rule group')
    parser.add_argument('--update_alert', help='update alert', dest='alert_id', default=None)
    parser.add_argument('-a','--aid', dest='alert_id', help='alert uid')

    parser.add_argument('--create_alert', action='store_true', help='create alert rule')
    parser.add_argument('--delete_alert', action='store_true', help='delete alert rule')
    return parser

def main(argv):
    argument_parser = SetupArgumentParser()
    options = argument_parser.parse_args()
    if options.get_alert:
        get_alert(options.alert_id)
    elif options.create_alert:
        create_alert(
            options.thresh_value,
            options.title,
            options.folder_name,
            options.rule_group,
            options.polarity,
            options.prefix,
            options.happi_name
        )
    elif options.delete_alert:
        delete_alert(options.alert_id)
    elif options.get_alert_group:
        get_alert_group(options.folder_name, options.rule_group)
    elif options.alert_id and options.thresh_value:
        update_alert(options.alert_id, thresh=options.thresh_value)
    elif options.alert_id and options.annotations:
        try:
            annotations = json.loads(options.annotations)
            if not isinstance(annotations, dict):
                raise ValueError("Annotations must be a dictionary")
            update_alert(options.alert_id,annotations=annotations)
        except json.JSONDecodeError:
            print("Error: Annotations must be a valid JSON")
            exit(1)
    elif options.alert_id and options.labels:
        try:
            labels = json.loads(options.labels)
            if not isinstance(labels, dict):
                raise ValueError("Labels must be a dictionary")
            update_alert(options.alert_id,labels=labels)
        except json.JSONDecodeError:
            print("Error: Labels must be a valid JSON")
            exit(1)
    elif options.alert_id and options.title:
        update_alert(options.alert_id, title=options.title)
    elif options.alert_id and options.pending:
        update_alert(options.alert_id, pending=options.pending)
    else:
        argument_parser.print_help()

main(sys.argv)
