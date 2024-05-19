async function getDanmus() {

    const response = await fetch('/api/danmus');
    const data = await response.json();

    const danmus = data.data;


    return {
        code: 0,
        msg: "no error",
        data: danmus
    };
}

async function getLastTalk() {

    const response = await fetch('/api/last-talk');
    const data = await response.json();

    const code = data.code;

    if (code !== 0) {
        return {
            code: code,
            msg: "error",
            data: null
        };
    }

    const lastTalk = data.data;


    return {
        code: 0,
        msg: "no error",
        data: lastTalk
    };
}

async function getLogs() {
    const response = await fetch('/api/logs');
    const data = await response.json();

    const code = data.code;

    if (code !== 0) {
        return {
            code: code,
            msg: "error",
            data: null
        };
    }

    const logs = data.data;

    return {
        code: 0,
        msg: "no error",
        data: logs
    };
}

async function getLog(logFilename) {
    const response = await fetch(`/api/log/${logFilename}`);
    const data = await response.json();

    const code = data.code;

    if (code !== 0) {
        return {
            code: code,
            msg: "error",
            data: null
        };
    }

    const logContent = data.data;

    return {
        code: 0,
        msg: "no error",
        data: logContent
    };
}

