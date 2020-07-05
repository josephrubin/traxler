"use strict";

const urlParams = new URLSearchParams(window.location.search);

function showShareMenu(e) {
  document.getElementById('shareMenu').style.visibility = "visible";
  document.getElementById('shareMenu').style.opacity = "1";
  // Stop the click event from closing the menu immediately.
  e.stopPropagation()
}

function hideShareMenu(e) {
  document.getElementById('shareMenu').style.visibility = "hidden";
  document.getElementById('shareMenu').style.opacity = "0";
}

function navigatorShare(e, name) {
  navigator.share({
    title: 'Stalk.page',
    text: "Check out " + name + "'s profile.",
    url: location.href,
  })
  hideShareMenu();
}

var t = null;

function navigatorClip(e) {
  document.getElementById('clip').style.display = "inline";
  document.getElementById('clip').value = location.href;
  document.getElementById('clip').select();
  document.execCommand('copy'); 
  document.getElementById('clip').style.display = "none";
  hideShareMenu();
  e.stopPropagation()
  if (t != null) {
    clearTimeout(t)
  }
  document.getElementById('share_bubble_img').src = "icon/check.png"
  t = setTimeout(function() {
    document.getElementById('share_bubble_img').src = "icon/share.png"
  }, 1000)
}

function navigatorBack(e) {
  window.history.back()
}

class Frame extends React.Component {
  render() {
    return <div className="frame student_page"
      onClick={hideShareMenu}
      style={{"backgroundColor": this.props.color}}>{this.props.children}</div>
  }
}

class ShareBubble extends React.Component {
  render() {
    return (
      <div className={"bubblebutton " + this.props.xtra} onClick={showShareMenu}>
        <img id="share_bubble_img" className={"icon " + this.props.xxtra} src={this.props.src} />
        <ShareMenu name={this.props.name} />
      </div>
    )
  }
}

class BackBubble extends React.Component {
  render() {
    return (
      <div className={"bubblebutton " + this.props.xtra} onClick={navigatorBack}>
        <img className={"icon back " + this.props.xxtra} src={this.props.src} />
      </div>
    )
  }
}

class SearchBar extends React.Component {
  focusMe() {
    document.getElementById('search_bar').focus();
  }

  render() {
    return (
      <div className="student_page search_bar" onClick={this.focusMe}>
        <img className={"icon search " + this.props.xxtra} src="icon/search.png" />
        <form className="form" method="GET" action="/search.html">
          <input id="search_bar" name="q" className="search student_page" defaultValue={this.props.fill} />
           <input type="hidden" name="token" value={urlParams.get("token")} />
          <input type="submit" />
        </form>
      </div>
    )
  }
}

class ShareMenu extends React.Component {
  render() {
    var navShare = ""
    if (navigator.share) {
      navShare = (
          <div onClick={(e) => navigatorShare(e, this.props.name)}>
            <span>Share</span>
            <img className="share_icon" src="icon/forward.png" />
          </div>
      )
    }
    return (
      <div id="shareMenu" className="student_page share_menu">
        {navShare}
        <div onClick={navigatorClip}>
          <span>Copy Link</span>
          <img className="share_icon" src="icon/copy.png" />
        </div>
      </div>
    )
  }
}

class Portrait extends React.Component {
  render() {
    return (
      <div className={"portrait " + this.props.xtra}>
        <img className="portrait student_page" src={this.props.src} />
      </div>
    )
  }
}

class Inbar extends React.Component {
  render() {
    return (
      <div className="inbar student_page" >
        <img className="icon_small" src={this.props.src} />
        <span className="alongside_icon_small">{this.props.text}</span>
      </div>
    )
  }
}

class InbarLink extends React.Component {
  render() {
    return (
      <div className="inbar student_page" >
        <img className="icon_small" src={this.props.src} />
        <a className="alongside_icon_small" href={"mailto:" + this.props.text}>{this.props.text}</a>
      </div>
    )
  }
}

class App extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      student: {
        name: null,
        study: null,
        email: null,
        college: null,
        degree: null,
        home: null
      }
    }
  }

  componentDidMount() {
    fetch("https://api.stalk.page/students/" + urlParams.get('!') + "?token=" + urlParams.get("token"))
      .then(res => res.json())
      .then(res => {
          var color = "#ffffff"
          switch (Number(res.student.year)) {
            case 21:
              color = "#fffef0"
              break;
            case 22:
              color = "#dbe9ff"
              break;
            case 23:
              color = "#ffeded"
              break;
            case 24:
              color = "#d4ffe4"
              break;
          }

          document.body.style.backgroundColor = color;
          document.body.style.overflow = "hidden";

          if (res.student.study == "Woodrow Wilson School") {
            res.student.study = "Public and International Affairs"
          }

          this.setState({
            isLoaded: true,
            student: res.student,
            color: color
          });
        },
        error => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      )
  }

  render() {
    return (
      <Frame color={this.state.color}>
        <div className="peacemaker">
          <BackBubble src="icon/back.png" />
          <SearchBar fill={this.state.student.netId} />
          <ShareBubble name={this.state.student.name} src="icon/share.png" xtra="fr" />
        </div>

        <Portrait xtra="student_page" src={"https://collface.deptcpanel.princeton.edu/img/" + this.state.student.image} />

        <div className="student_page spacer_one"></div>

        <h1 className="student_page">{this.state.student.name}</h1>
        <h2 className="student_page">{this.state.student.study + ", " + this.state.student.degree + " " + this.state.student.year}</h2>

        <div className="inbar_group student_page">
          <InbarLink src="icon/mail.png" text={this.state.student.netId + "@princeton.edu"} />
          <Inbar src="icon/place.png" text={this.state.student.college} />
        </div>
        <input id="clip" className="clip" />
      </Frame>
    )
  }
}

// <Inbar src="icon/place.png" text={this.state.student.home} />

ReactDOM.render(
  <App />,
  document.getElementById('root')
);