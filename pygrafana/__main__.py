import sys, argparse, json
from happi import Client
from happi.item import OphydItem
from happi.errors import EnforceError
from typing import List
from .grafana import fetch_alert, create_alert_rule, delete_alert_rule, fetch_alert_group, update_alert_rule
from .serialize_alert import ProvisionedAlertRule, AlertGroup
from .create_alert import AlertCreater

fms_happi_database = "fms_test.json"

def create_alert(value, title, folder_name, rule_group, polarity, pv, happi_name):
    ac = AlertCreater()
    if polarity == None:
        ac.create_alert(
            value,
            alert_title=title,
            folder_name=folder_name,
            rule_group=rule_group,
            pv=pv,
            happi_name=happi_name)
    else:
        ac.create_alert("A new alert test")

def delete_alert(alert_uid):
    delete_alert_rule(alert_uid)

def update_alert(alert_uid, annotations=None, title=None, pending=None, labels=None):
    alert = fetch_alert(alert_uid)
    alert_rule = ProvisionedAlertRule.parse_raw(alert)

    if annotations != None:
        alert_rule.annotations = annotations
    elif title != None:
        alert_rule.title = title 
    elif pending != None:
        alert_rule.for_ = pending
    elif labels != None:
        alert_rule.labels = labels
    else:
        print("No update parameters provided, exit")
        exit
    #alert_rule.labels = dict(subsystem="fmsv2")

    update_alert_rule(alert_uid, json.dumps(alert_rule.dict(by_alias=True)))

def get_alert_group(folder_uid, group):
    #print(group)
    alert_group = fetch_alert_group(folder_uid, group) 
    #print(alert_group)
    alert = AlertGroup.parse_obj(alert_group)
    print(alert) 

def get_alert(alert_uid):
    alert = fetch_alert(alert_uid)
    alert_rule = ProvisionedAlertRule.parse_raw(alert)
    print(alert_rule)

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
    #parser.add_argument('--update_alert', help='update alert', choices=["title", "annotations","pending", "labels"], default=None)
    parser.add_argument('-a','--aid', dest='alert_id', help='alert uid')

    parser.add_argument('--create_alert', action='store_true', help='create alert rule')
    parser.add_argument('--delete_alert', action='store_true', help='delete alert rule')
    return parser

def main(argv):
    #if options.alert_id == None:
    #    print("you must provide an alert ID -a 32edcerafs.\n")
    #    exit    
    argument_parser = SetupArgumentParser()
    options = argument_parser.parse_args()
    #print(options)
    #print(sys.argv)
    if options.get_alert:
        get_alert(options.alert_id)
    elif options.create_alert:
        create_alert(
            options.thresh_value,
            options.alert_title,
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

#python -m fms --create_alert -t flood11 -f xrt -r xrt_pcw -v 0 -pv MR1K1:BEND:MMS:XUP.RBV
