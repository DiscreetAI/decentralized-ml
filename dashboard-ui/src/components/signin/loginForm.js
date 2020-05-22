// Generated by https://pagedraw.io/pages/7992
import React from 'react';
import ReactDOM from 'react-dom';
import { Link, withRouter } from "react-router-dom";
import Reflux from 'reflux';

import AuthStore from './../../stores/AuthStore';
import AuthActions from './../../actions/AuthActions';

import './common.css';

class LoginForm extends Reflux.Component {

  constructor(props) {
    super(props);
    this.store = AuthStore;
  }

  componentWillUpdate(nextProps, nextState) {
    var isAuthenticated = nextState['isAuthenticated'];
    if (isAuthenticated) {
      this.props.history.push("dashboard");
    }
  }

  _handleSubmit(event) {
    event.preventDefault();

    let form = document.getElementById('loginForm');
    if (form.reportValidity()) {
      AuthActions.login(
        ReactDOM.findDOMNode(this.refs.email).value,
        ReactDOM.findDOMNode(this.refs.password).value
      );
    }
  }

  render() {
    var errorMessage = "";
    var waitMessage = "";
    var loginButton = (<button type="submit" onClick={this._handleSubmit.bind(this)} className="btn btn-dark-alt">Sign In</button>);

    if (this.state.hasError) {
      errorMessage = (
        <div className='alert alert-danger padding-bottom alert-dismissible fade show' role="alert">
          { this.state.error }
        </div>
      );
    }

    if (this.state.waiting) {
      loginButton = (<button type="submit" onClick={this._handleSubmit.bind(this)} className="btn btn-dark-alt" disabled>Sign In</button>);
      waitMessage = (<p id="wait" className="mt-3"><b>Please wait...</b></p>);
    }

    return (
      <div>
        <form id="loginForm" className="login-form col-12 col-sm-12 col-md-4 offset-md-4">

          { errorMessage }

          <div className="form-group">
            <label>Email address</label>
            <input type="email" ref="email" className="form-control" id="inputEmail" placeholder="Enter email" required/>
          </div>

          <div className="form-group">
            <label>Password</label>
            <input type="password" ref="password" className="form-control" id="inputPassword" placeholder="Enter password" required/>
          </div>

          <div className="form-group text-center">
            { loginButton }
            { waitMessage }
            
          </div>

          <div className="form-group text-center text-dark">
            New here? <Link to="signup" href="# text-primary">Sign up!</Link>
          </div>

        </form>
      </div>
    );
  }
}

export default withRouter(LoginForm);
