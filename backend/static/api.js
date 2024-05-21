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

async function replyByBid(bid) {
    // post
    const response = await fetch(`/api/reply/${bid}`, {
        method: 'POST',
    });
    const data = await response.json();

    const code = data.code;

    if (code !== 0) {
        return {
            code: code,
            msg: "error"
        };
    }
    return {
        code: 0,
        msg: "no error"
    };
}


async function sendTestDanmu(content) {
    // post
    const response = await fetch(`/api/test/danmu/${content}`);
    const data = await response.json();

    const code = data.code;

    if (code !== 0) {
        return {
            code: code,
            msg: "error"
        };
    }
    return {
        code: 0,
        msg: "no error"
    };
}

async function getLiveRoomInfo() {
    // post
    const response = await fetch(`/api/live-room-info`);
    const data = await response.json();

    if (data.code !== 0) {
        return {
            code: code,
            msg: "error"
        };
    }
    return {
        code: 0,
        msg: "no error",
        data: data.data
    };
}

async function getConfig() {
    const response = await fetch('/api/config');
    const data = await response.json();

    if (data.code !== 0) {
        return {
            code: code,
            msg: "error"
        };
    }
    return {
        code: 0,
        msg: "no error",
        data: data.data
    };
}

async function getComponentSubtypeConfig(componentType, subtype) {
    const response = await fetch(`/api/config/component/${componentType}/subtype/${subtype}`);
    const data = await response.json();

    if (data.code !== 0) {
        return {
            code: code,
            msg: "error"
        };
    }
    return {
        code: 0,
        msg: "no error",
        data: data.data
    };
}