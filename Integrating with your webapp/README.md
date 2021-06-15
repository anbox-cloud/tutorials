# Integrate Anbox Cloud in your web application

The dashboard included in Anbox Cloud is great to get started but writing your own web application

## 0. AMC

`amc` is the main tool you'll be using to interact with Anbox Cloud.

 > `amc` is a simple wrapper over `ams` HTTP API. Everything you can do with `amc` can also be
 > done through the API 

### Accessing AMC

Depending on how you deployed Anbox Cloud, `amc` can be accessed in different ways

**Anbox Cloud Appliance (AWS Marketplace):**
```sh
$ ssh ubuntu@<instance IP>
$ amc help
```

**Juju based deployment:**
```sh
$ juju ssh ams/0
$ amc help
```

## 1. Creating the application

Create a directory and place a file named `manifest.yaml` in it.

```sh
$ mkdir my-android10-app
$ touch my-android10-app/manifest.yaml
```

And copy the following in `manifest.yaml`:

```yaml
name: my-android10-app
instance-type: a2.3
```

Then use `amc` to create the application:

```sh
$ amc application create ./my-android10-app
```

`amc` will take a few minutes to prepare the application (apply security patches, optimize image size, run hooks, etc).
You can monitor progress by running `amc application list` or block until it is ready with `amc wait -c status=ready my-android10-app`


## 2. Building a simple web app to stream your Android applications

Create a simple webpage containing an element with the ID `anbox-stream`. This is where the video stream will be displayed:

```html
<!DOCTYPE html>
<html>
<head>
    <meta content="text/html;charset=utf-8" http-equiv="Content-Type">
    <meta content="utf-8" http-equiv="encoding">
    <title>Anbox Streaming SDK Example</title>
</head>
<body>
    <div id="anbox-stream"></div>
</body>
```

Then include the stream SDK:

```sh
$ git clone https://github.com/anbox-cloud/anbox-streaming-sdk.git
```

```html
<!DOCTYPE html>
<html>
<head>
    <meta content="text/html;charset=utf-8" http-equiv="Content-Type">
    <meta content="utf-8" http-equiv="encoding">
    <title>Anbox Cloud Tutorial</title>
    <script src="./anbox-streaming-sdk/js/anbox-stream-sdk.js"></script>
</head>
<body>
    <div id="video-stream"></div>
</body>
```

This will inject two classes in the `window` object.
 * `window.AnboxStream` is the main object you'll interact with. It handles the actual WebRTC communication
 * `window.AnboxStreamGatewayConnector` is a middleware that handles authentication for the Stream Gateway. If you want to later add your own authentication and application layer, you can implement your own connector without having to change the rest of the SDK

----

Streaming works as follows:
 1. Authenticate with the Stream Gateway
 2. Pick an application and configure the stream
 3. Let the `AnboxStream` class handle the WebRTC setup

#### 1. Authenticate with the Stream Gateway

Authentication is done through a **connector**. This is a small class that is used later on by the AnboxStream object
and whose purpose is to handle authentication. A connector for the Stream Gateway is provided, but you must write
your own to use a middleware (this is covered in the next step of the tutorial).

The Stream Gateway has a token based authentication. You can obtain a new token with the following command:
```sh
# Anbox Cloud Appliance based
$ anbox-cloud-appliance gateway account create my-account-name

# Juju based
$ juju run-action anbox-stream-gateway/0 create-auth-token service=my-account-name --wait
```

Next, create the connector:
```js
const connector = new AnboxStreamGatewayConnector({
    url : 'gateway.url.net',
    authToken: 'YOUR_AUTH_TOKEN',
    session: {
        app: "my-android10-app",
    },
});
```

> If you've deployed Anbox Cloud through the AWS marketplace image, you can replace `gateway.url.net` by `https://<ec2_ip>`.
> On Juju based deployments, you would use the IP address of `anbox-stream-gateway-lb` has such: `https://<lb_ip>`

----

Create a new `AnboxStream` object:
```js
let stream = new AnboxStream({
    connector: connector,
    targetElement: "anbox-stream",
    screen: {
        width: 1280,
        height: 720,
        fps: 25,
    },
    callbacks: {
        error: error => {
            console.error("Some error occurred: ", error);
        }
    }
});
```

> All options are documented inline in the SDK source

Then when everything is ready you can initiate the connection with:
```js
stream.connect();
```

## Running

You can use your favorite web server here. Here's a one liner for [npm serve](https://www.npmjs.com/package/serve):
```sh
$ docker run -itp 5001:5000 -v $PWD:/src node:latest npx --yes serve /src/
```


### References
 * [Creating and managing application](https://anbox-cloud.io/docs/manage/managing-applications)