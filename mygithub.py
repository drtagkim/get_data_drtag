# -*- coding:utf-8 -*-
# ##################################################################
# PyGithub frontend
# Author: Taekyung Kim
# Requirement:
#    pip install pygithub
#    pip install unicodecsv
# ##################################################################
from github import GithubException
from github import Github
from sys import stdout
import unicodecsv
import sys
import time
# token = "e9c9c32be88a969c83ebf1aa3a28ea340c72ca57"
# Read: https://help.github.com/articles/creating-an-access-token-for-command-line-use/
progress_mark = "LOVE"

def create_connection(token):
    '''
|  Github 연결
|  반환: github.MainClass.Github
|  g.rate_limiting
    '''
    g = Github(token,timeout=300)
    return g
def get_repository_id(repository):
    return repository.id,repository.full_name.replace("/","__")
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
    rep_id, rep_fn = get_repository_id(repository)
    rv_contributors = []
    cnt = 0
    try:
        for contributor in repository.get_contributors():
            output = [rep_id,rep_fn]
            stdout.write("\r%s"%progress_mark[cnt % 4])
            stdout.flush()
            cnt += 1
            user = analyze_user(contributor)
            output.extend(user)
            rv_contributors.append(output)
        stdout.write("\r...Complete")
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
    rep_id, rep_fn = get_repository_id(repository)
    rv_contributions = []
    try:
        cnt = 0
        for contribution in repository.get_stats_contributors():
            author = analyze_user(contribution.author) #dict
            user_id = contribution.author.id
            stdout.write("\r%s"%progress_mark[cnt % 4])
            stdout.flush()
            cnt += 1
            if contribution.weeks != None:
                for week in contribution.weeks:
                    output = [rep_id,user_id]
                    week_str = str(week.w).split(" ")[0] #year-month-day
                    amount_add = week.a
                    amount_delete = week.d
                    amount_change = week.c
                    output.extend([week_str,amount_add,amount_delete,amount_change])
                    rv_contributions.append(output)
        stdout.write("\r...Complete")
        stdout.write("\n")
        stdout.flush()
    except GithubException,e:
        print e
    except TypeError:
        pass
    return rv_contributions
def get_stat_code_frequency(repository):
    rv_cf = []
    rep_id, rep_fn = get_repository_id(repository)
    try:
        cnt = 0
        for cf in repository.get_stats_code_frequency():
            week = str(cf.week).split(" ")[0]
            nadd = cf.additions
            ndelete = cf.deletions
            rv_cf.append([rep_id,week,nadd,ndelete])
            stdout.write("\r%s"%progress_mark[cnt % 4])
            stdout.flush()
        stdout.write("\r...Complete")
        stdout.write("\n")
        stdout.flush()
    except GithubException,e:
        print e
    except TypeError:
        pass
    return rv_cf
def get_info_issues(repository):
    rep_id, rep_fn = get_repository_id(repository)
    rv_issues = []
    rv_events = []
    rv_comments = []
    try:
        cnt = 0
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
            rv_issues.append([rep_id,iid,inumber,iuser_id,ititle,icreated_at,iclosed_at,iclosed_by])
            stdout.write("\r%s"%progress_mark[cnt % 4])
            stdout.flush()
            for event in issue.get_events():
                try:
                    eby = event.actor.id
                    ecreated_at = str(event.created_at)
                    eevent = event.event
                    eid = event.id
                    rv_events.append([rep_id,iid,eid,ecreated_at,eby,eevent])
                except:
                    pass
            for comment in issue.get_comments():
                #cbody = comment.body
                try:
                    cid = comment.id
                    cuser = comment.user.id
                    ccreated_at = str(comment.created_at)
                    rv_comments.append([rep_id,iid,cid,ccreated_at,cid])
                except:
                    pass
        stdout.write("\r...Complete")
        stdout.write("\n")
        stdout.flush()
    except GithubException,e:
        print e
    except TypeError:
        pass
    return rv_issues,rv_events,rv_comments
def export_stat_contributions(contribution_data,filename):
    f = open(filename,'wb')
    w = unicodecsv.writer(f,encoding='utf-8')
    w.writerow(['repository_id','user_id','weekid','nadd','ndelete','nchange'])
    w.writerows(contribution_data)
    f.close()
def export_contributors(contributor_data,filename):
    f = open(filename,'wb')
    w = unicodecsv.writer(f,encoding='utf-8')
    w.writerow(['repository_id','repository_fullname','contributor_id','contributor_name','contributor_email','contributor_created_at','contributor_nfollowers','contributor_nfollowing'])
    w.writerows(contributor_data)
    f.close()        
def export_issue_info(issue_info,filename):
    f = open(filename,'wb')
    w = unicodecsv.writer(f,encoding='utf-8',delimiter='\t')
    w.writerow(['repository_id','issue_id','issue_number','issue_by','issue_title','issue_created_at','issue_closed_at','issue_closed_by'])
    w.writerows(issue_info)
    f.close()
def export_issue_comment(issue_comment,filename):
    f = open(filename,'wb')
    w = unicodecsv.writer(f,encoding='utf-8',delimiter='\t')
    w.writerow(['repository_id','issue_id','comment_created_at','comment_by'])
    w.writerows(issue_comment)
    f.close()
def export_issue_event(issue_event,filename):
    f = open(filename,'wb')
    w = unicodecsv.writer(f,encoding='utf-8')
    w.writerow(['repository_id','issue_id','event_id','event_created_at','event_by','event_verb'])
    w.writerows(issue_event)
    f.close()
def export_code_frequency(code_frequency,filename):
    f = open(filename,'wb')
    w = unicodecsv.writer(f,encoding='utf-8')
    w.writerow(['repository_id','weekstr','nadd','ndelete'])
    w.writerows(code_frequency)
    f.close()
def main(my_token,full_name=None):
    mygit = create_connection(my_token)
    print "======================="
    refresh_rate_limit(mygit)
    print "YOUR RATE LIMIT:"
    print_rate_limit(mygit)
    print "RESET AT:"
    print_rate_limit_reset_time(mygit)
    print "======================="
    if full_name == None:
        rep_name = raw_input("Type repository full name >>>")
    else:
        rep_name = full_name
    rep = get_repository_by_name(mygit,rep_name)
    tag = rep.full_name.replace("/","__")
    fname_contributors = "%s_contributor_list.csv"%(tag,)
    fname_contributions = "%s_contribution.csv"%(tag,)
    fname_issue_info = "%s_issue_info.tsv"%(tag,)
    fname_issue_event = "%s_issue_event.csv"%(tag,)
    fname_issue_comment = "%s_issue_comment.tsv"%(tag,)
    fname_code_frequency = "%s_code_frequency.csv"%(tag,)
    print "[STEP 1] Getting the list of contributors"
    contributors = get_contributors(rep)
    print "[STEP 2] Getting contributions"
    contributions = get_stat_contributors_by_rep(rep)
    print "[STEP 3] Getting code frequency stats"
    code_frequency = get_stat_code_frequency(rep)
    print "[STEP 4] Getting issue information"
    issue_info,events,comments = get_info_issues(rep)
    export_contributors(contributors,fname_contributors)
    export_stat_contributions(contributions,fname_contributions)
    export_code_frequency(code_frequency,fname_code_frequency)
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
    if mygit.rate_limiting[0] <= 500:
        waiting_time = mygit.rate_limiting_resettime - time.time()
        print "Waiting for %f seconds for reset" % waiting_time
        time.sleep(waiting_time)
        
def save_repos_data(data,fname):
    rv = []
    for d in data:
        rv.append([d.id,d.full_name,d.html_url])
    f = open(fname,'wb')
    w = unicodecsv.writer(f,encoding='utf-8')
    w.writerow(['repository_id','repository_fullname','repository_url'])
    w.writerows(rv)
    f.close()
def acquire_all_repos(my_token,dir_name,page_start=None,page_end=None):
    mygit = create_connection(my_token)
    all_repos = mygit.get_repos()
    if page_start == None:
        page_cnt = 0
    else:
        page_cnt = page_start
    if page_end == None:
        page_end = -1
    rt = mygit.rate_limiting_resettime
    while 1:
        stdout.write("%d"%(page_cnt))
        stdout.flush()
        repo = all_repos.get_page(page_cnt)
        if len(repo) == 0:
            break
        fname = "%s/%010d_git_repo.csv"%(dir_name,page_cnt,)
        stdout.write(",")
        stdout.flush()
        save_repos_data(repo,fname)
        stdout.write(".")
        stdout.flush()
        if page_end >= 0 and page_end == page_cnt:
            break
        page_cnt += 1
        if mygit.rate_limiting[0] <= 10:
            diff = rt - time.time() + 10
            stdout.write("#")
            stdout.flush()
            time.sleep(diff)
            a = mygit.get_rate_limit()
            rt = mygit.rate_limiting_resettime
        else:
            diff = rt - time.time()
            if diff <= 0:
                a = mygit.get_rate_limit()
                rt = mygit.rate_limiting_resettime
if __name__ == "__main__":
    '''
|  전체 리스트를 다 받는다면
|  $ python mygithub.py 2 your_token.txt output_dir
|  만약 중간에서 다시 시작해야 하면 (e.g., 12 page)
|  $ python mygithub.py 2 your_token.txt output_dir 12
|  끝나는 페이지를 정한다면 (e.g., 12~20까지)
|  $ python mygithub.py 2 your_token.txt output_dir 12 20
|  특정한 repository의 full_name입력해서 데이터 추출하려면
|  $ python mygithub.py 1 your_token.txt
    '''
    try:
        choice = sys.argv[1]
        token_file = sys.argv[2]
    except:
        print "$ python 1 mygithub.py 1 your_token.txt"
        print "$ python 2 mygithub.py 2 your_token.txt"
        sys.exit(0)
    assert type(token_file) == str,"Token filename should be string."
    my_token = ''
    try:
        f = open(token_file)
        my_token = f.readline()
        f.close()
    except IOError:
        print "Your token file has a problem."
        sys.exit(0)
    if len(my_token) <=0:
        print "Your toke file has a problem"
        sys.exit(0)
    # EXECUTION
    if choice == '1':
        main(my_token)
    elif choice == '2':
        dir_name = sys.argv[3]
        if len(sys.argv) == 5:
            page_start = int(sys.argv[4])
        elif len(sys.argv) == 6:
            page_start = int(sys.argv[4])
            page_end = int(sys.argv[5])
        else:
            page_start = None
            page_end = None
        acquire_all_repos(my_token,dir_name,page_start=page_start,page_end=page_end)
    elif choice == '3':
        full_name_fname = sys.argv[3]
        f = open(full_name_fname)
        reader = unicodecsv.reader(f,encoding='utf-8')
        full_names = []
        for r in reader:
            full_names.append(r[0])
        f.close()
        for fn in full_names:
            main(my_token,fn)
# === END OF PROGRAM ===