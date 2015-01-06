# -*- coding:utf-8 -*-
# PyGithub frontend
# Author: Taekyung Kim
from github import GithubException
from github import Github
from sys import stdout
token = "e9c9c32be88a969c83ebf1aa3a28ea340c72ca57"


def create_connection():
    '''
|  Github 연결
|  반환: github.MainClass.Github
|  g.rate_limiting
    '''
    g = Github(token,timeout=300)
    return g
def refresh_rate_limit(git):
    git.get_rate_limit()
def print_rate_limit(git):
    a = git.rate_limiting[0]
    if a <= 0:
        refresh_rate_limit()
    a = git.rate_limiting[0]
    print a
    
def print_rate_limit_reset_time(git):
    from datetime import datetime
    print datetime.fromtimestamp(git.rate_limiting_resettime).strftime("%Y-%m-%d %H:%M:%S")

def get_repository_by_name(git,repo_name):
    '''
|  For example,
|  >>> get_repository_by_name(git,"sampsyo/beets")
    '''
    try:
        return git.get_repo(repo_name)
        print "Rate Limiting = %d" % (git.rate_limiting[0])
    except:
        print "Error"
        return None
def analyze_user(user):
    '''
|  http://jacquev6.net/PyGithub/v1/github_objects/NamedUser.html#github.NamedUser.NamedUser
    '''
    rv = {}
    rv['created_at'] = str(user.created_at).split(" ")[0]
    rv['email'] = user.email
    rv['nfollowers'] = user.followers
    rv['nfollowing'] = user.following
    rv['id'] = user.id
    rv['name'] = user.name
    return [rv['id'],rv['name'],rv['email'],rv['created_at'],rv['nfollowers'],rv['nfollowing']]
def get_contributors(repository):
    rv_contributors = []
    try:
        for contributor in repository.get_contributors():
            stdout.write("U")
            stdout.flush()
            user = analyze_user(contributor)
            rv_contributors.append(user)
        stdout.write("\n")
        stdout.flush()
    except GithubException,e:
        print e
    except TypeError:
        pass
    return rv_contributors
def get_stat_contributors_by_rep(repository):
    '''
|  100 page까지 limit가 걸린다.
    '''

    rv_contributions = []
    try:
        for contribution in repository.get_stats_contributors():
            author = analyze_user(contribution.author) #dict
            user_id = contribution.author.id
            stdout.write("C")
            stdout.flush()
            if contribution.weeks != None:
                for week in contribution.weeks:
                    output = [user_id,]
                    week_str = str(week.w).split(" ")[0] #year-month-day
                    amount_add = week.a
                    amount_delete = week.d
                    amount_change = week.c
                    output.extend([week_str,amount_add,amount_delete,amount_change])
                    rv_contributions.append(output)
        stdout.write("\n")
        stdout.flush()
    except GithubException,e:
        print e
    except TypeError:
        pass
    return rv_contributions
def get_info_issues(repository):
    rv_issues = []
    rv_events = []
    rv_comments = []
    try:
        for issue in repository.get_issues():
            iuser = issue.user
            iid = issue.id
            inumber = issue.number
            iuser_id = iuser.id
            ititle = issue.title
            #ibody = issue.body
            icreated_at = str(issue.created_at)
            iclosed_at = str(issue.closed_at)
            try:
                iclosed_by = issue.closed_by.id
            except:
                iclosed_by = -1
            rv_issues.append([iid,inumber,iuser_id,ititle,icreated_at,iclosed_at,iclosed_by])
            stdout.write("I")
            stdout.flush()
            for event in issue.get_events():
                eby = event.actor.id
                ecreated_at = str(event.created_at)
                eevent = event.event
                eid = event.id
                rv_events.append([iid,eid,ecreated_at,eby,eevent])
            for comment in issue.get_comments():
                #cbody = comment.body
                cid = comment.id
                cuser = comment.user.id
                ccreated_at = str(comment.created_at)
                rv_comments.append([iid,cid,ccreated_at,cid])
        stdout.write("\n")
        stdout.flush()
    except GithubException,e:
        print e
    except TypeError:
        pass
    return rv_issues,rv_events,rv_comments
def export_stat_contributions(contribution_data,filename):
    import unicodecsv
    f = open(filename,'wb')
    w = unicodecsv.writer(f,encoding='utf-8')
    w.writerow(['user_id','weekid','nadd','ndelete','nchange'])
    w.writerows(contribution_data)
    f.close()
def export_contributors(contributor_data,filename):
    import unicodecsv
    f = open(filename,'wb')
    w = unicodecsv.writer(f,encoding='utf-8')
    w.writerow(['contributor_id','contributor_name','contributor_email','contributor_created_at','contributor_nfollowers','contributor_nfollowing'])
    w.writerows(contributor_data)
    f.close()        
def export_issue_info(issue_info,filename):
    import unicodecsv
    f = open(filename,'wb')
    w = unicodecsv.writer(f,encoding='utf-8',delimiter='\t')
    w.writerow(['issue_id','issue_number','issue_by','issue_title','issue_created_at','issue_closed_at','issue_closed_by'])
    w.writerows(issue_info)
    f.close()
def export_issue_comment(issue_comment,filename):
    import unicodecsv
    f = open(filename,'wb')
    w = unicodecsv.writer(f,encoding='utf-8',delimiter='\t')
    w.writerow(['issue_id','comment_created_at','comment_by'])
    w.writerows(issue_comment)
    f.close()
def export_issue_event(issue_event,filename):
    import unicodecsv
    f = open(filename,'wb')
    w = unicodecsv.writer(f,encoding='utf-8')
    w.writerow(['issue_id','event_id','event_created_at','event_by','event_verb'])
    w.writerows(issue_event)
    f.close()
def main():
    mygit = create_connection()
    print "======================="
    refresh_rate_limit(mygit)
    print "YOUR RATE LIMIT:"
    print_rate_limit(mygit)
    print "RESET AT:"
    print_rate_limit_reset_time(mygit)
    print "======================="
    rep_name = raw_input("Type repository full name >>>")
    rep = get_repository_by_name(mygit,rep_name)
    tag = raw_input("Type prefix >>>")
    fname_contributors = "%s_contributor_list.csv"%(tag,)
    fname_contributions = "%s_contribution.csv"%(tag,)
    fname_issue_info = "%s_issue_info.tsv"%(tag,)
    fname_issue_event = "%s_issue_event.csv"%(tag,)
    fname_issue_comment = "%s_issue_comment.tsv"%(tag,)
    print "[STEP 1] Getting the list of contributors"
    contributors = get_contributors(rep)
    print "[STEP 2] Getting contributions"
    contributions = get_stat_contributors_by_rep(rep)
    print "[STEP 3] Getting issue information"
    issue_info,events,comments = get_info_issues(rep)
    export_contributors(contributors,fname_contributors)
    export_stat_contributions(contributions,fname_contributions)
    export_issue_info(issue_info,fname_issue_info)
    export_issue_comment(comments,fname_issue_comment)
    export_issue_event(events,fname_issue_event)
    print "DONE"
    print "======================="
    refresh_rate_limit(mygit)
    print "YOUR RATE LIMIT:"
    print_rate_limit(mygit)
    print "RESET AT:"
    print_rate_limit_reset_time(mygit)
    print "======================="
if __name__ == "__main__":
    main()