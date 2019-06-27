import React from 'react';
import Reflux from 'reflux';

import NotFoundPage from './notFoundPage';
import RepoStatus from './repo/repoStatus';
import RepoLogs from './repo/repoLogs';
import RepoModels from './repo/repoModels';
import { Link } from 'react-router-dom';

import RepoDataStore from './../stores/RepoDataStore';
import RepoDataActions from './../actions/RepoDataActions';

import RepoLogsStore from './../stores/RepoLogsStore';
import RepoLogsActions from './../actions/RepoLogsActions';

import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';

import Endpoints from './../constants/endpoints.js';


class Repo extends Reflux.Component {
  constructor(props) {
    super(props);
    this.stores = [RepoDataStore, RepoLogsStore];

    const { match: { params } } = this.props;
    this.repoId = params.repoId;
    this.url = null;
    console.log(this.repoId)
    fetch(
      Endpoints["dashboardGetExploraURL"], {
        method: 'POST',
        dataType:'json',
        headers: {
          'Content-Type':'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          'repo_name': this.repoId
        })
      }
    )
    .then(r => r.json())
    .then(r => {
      console.log(r)
      this.url = r;
      console.log(this.url);
    });
  }

  componentDidMount() {
    const { match: { params } } = this.props;
    const repoId = params.repoId;

    RepoDataActions.fetchRepoData(repoId);
    RepoLogsActions.fetchRepoLogs(repoId);

    
  }

  render() {
    // if (this.state.error !== false) {
    //   return (
    //     <div className="text-center"><p>
    //       Error: {this.state.error}</p>
    //     </div>
    //   );
    // }

    if (this.state.loading === true) {
      return (
        <div className="text-center text-secondary">
          <FontAwesomeIcon icon="sync" size="lg" spin />
        </div>
      );
    }

    if (!this.state.repoWasFound) {
      return <NotFoundPage />
    }
    console.log("HI");
    let createdLessThan10MinutesAgo = Math.floor(Date.now()/1000) < (this.state.repoData.CreatedAt + 60*10);
    return (
      <div className="pb-5">
        <div className="row">
          <div className="col-1"></div>
          <div className="col-8">
            <h3>{this.state.repoData.Name}</h3>
            <p>{this.state.repoData.Description}</p>
          </div>
          <div className="col-2 text-right">
            <RepoStatus repoId={this.state.repoData.Id} isDeploying={createdLessThan10MinutesAgo} />
            <p className="mt-3"><a href={this.url} className="btn btn-xs btn-dark"><b>Open Explora</b></a></p>
          </div>
        </div>

        <div className="row mt-4">
          <div className="col-1"></div>
          <div className="col-10">
            <div className="card">
              <div className="card-header">
                <h5>Exploratory Data (ED)</h5>
                <p className="mb-0"><small>Example data that each client should be storing locally. The deployed models should be able to train on this structure.</small></p>
              </div>
              <div className="card-body text-center mt-3">
                <p className="card-text"><b>No exploratory data yet.</b></p>
                <p><small>(Feature in development.)</small></p>
                <div className="row mt-4">
                  <div className="col-4"></div>
                  <div className="col-2 text-center">
                    <a href="#upload-ed" className="btn btn-primary disabled">Upload ED</a>
                  </div>
                  <div className="col-2 text-center">
                    <Link to={"/explora/"+this.state.repoData.Id} className="btn btn-dark">Explore ED</Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <RepoModels logs={this.state.repoLogs} />

        <RepoLogs logs={this.state.repoLogs} />

      </div>
    )
  }
}

export default Repo;
