var Endpoints = {
  'eauthLogin': 'https://eauth.dataagora.com/auth/login/',
  'eauthUser': 'https://eauth.dataagora.com/auth/user/',
  'eauthRegistration': 'https://eauth.dataagora.com/auth/registration/',
  'eauthLogout': 'https://eauth.dataagora.com/auth/logout/', // Not used with JWT.

  'dashboardFetchReposRemaining': 'https://mf1cxij8x6.execute-api.us-west-1.amazonaws.com/dev/userdata',
  'dashboardCreateNewRepo': 'https://mf1cxij8x6.execute-api.us-west-1.amazonaws.com/dev/repo',
  'dashboardFetchAllRepos': 'https://mf1cxij8x6.execute-api.us-west-1.amazonaws.com/dev/repos',
  'dashboardFetchRepoData': 'https://mf1cxij8x6.execute-api.us-west-1.amazonaws.com/dev/repo/',
  'dashboardFetchRepoLogs': 'https://mf1cxij8x6.execute-api.us-west-1.amazonaws.com/dev/logs/',
  'dashboardFetchCoordinatorStatus': 'https://mf1cxij8x6.execute-api.us-west-1.amazonaws.com/dev/coordinator/status/',
  'dashboardGetDownloadModelURL': 'https://mf1cxij8x6.execute-api.us-west-1.amazonaws.com/dev/model',
};

export default Endpoints;
