import { configureStore, createSlice } from '@reduxjs/toolkit'
import { Bot, app_store_bot, block_bot_ids} from '../components/interface';
// https://redux-toolkit.js.org/api/configureStore

const BOT_LIST = "BOT_LIST";
const CURRENT_BOT = "CURRENT_BOT";
const APP_STORE_BOT_LIST = "APP_STORE_BOT_LIST";


// 加载数据
function loadStorageJson (key: string, default_value: any) {
    const value = localStorage.getItem(key);
    let result = default_value
    if (value) {
        result = JSON.parse(value);
    }
    return result;
}

// 存储中间件: bot_list
function createLocalStorageMiddleware() {
    return (store: any) => (next: any) => (action: any) => {
        const result = next(action);
        // 存储到localStorage
        // bot_list
        const state = store.getState();
        if (state.data.bot_list) {
            const json = JSON.stringify(state.data.bot_list);
            localStorage.setItem(BOT_LIST, json);
        }
        // current_bot
        if (state.data.current_bot) {
            const json = JSON.stringify(state.data.current_bot);
            localStorage.setItem(CURRENT_BOT, json);
        }
        // app_store_bot_list
        if (state.data.app_store_bot_list) {
            const json = JSON.stringify(state.data.app_store_bot_list);
            localStorage.setItem(APP_STORE_BOT_LIST, json);
        }
        return result;
    };
}

interface BotReduxState {
    current_bot: Bot | null;
    bot_list: any [],
    app_store_bot_list: any []
}

// Slice
const ReduxSlice = createSlice({
    name: 'xxx',
    initialState: {
        current_bot: loadStorageJson(CURRENT_BOT, app_store_bot),
        bot_list: loadStorageJson(BOT_LIST, []),
        app_store_bot_list: loadStorageJson(APP_STORE_BOT_LIST, [])
    },
    reducers: {
        // 打开机器人
        open_bot: (state: BotReduxState, action) => {
            // 如果机器人不在列表中 & 不是 app_store，则添加到列表中
            let new_bot: Bot = action.payload
            if (!state.bot_list.find((bot: Bot) => bot.id === new_bot.id)) {
                if (!block_bot_ids.includes(new_bot.id)) {
                    console.log('add bot to bot_list');
                    state.bot_list = [new_bot, ...state.bot_list];
                    // 收藏bot
                    // apiBotLike(new_bot.id).then(function(res){});
                }
            }
            state.current_bot = new_bot;
        },
        // 置顶机器人
        top_bot: (state, action) => {
            const bot = action.payload;
            if (state.bot_list[0].id != bot.id) {
                state.bot_list = [bot, ...state.bot_list.filter((b: Bot) => b.id !== bot.id)];
            }
        },
        // 删除机器人
        delete_bot: (state, action) => {
            // 如果当前机器人是被删除的机器人，则将current_bot设置为应用中心
            if (state.current_bot && state.current_bot.id === action.payload.id) {
                state.current_bot = app_store_bot;
            }
            state.bot_list = [...state.bot_list.filter((bot: Bot) => bot.id !== action.payload.id)];
            // 取消收藏bot
            // apiBotUnlike(action.payload.id).then(function(res){});
        },
        // 更新收藏机器人
        update_bot_list: (state, action) => {
        },
        // 更新app store 的机器人
        update_app_store_bot_list: (state, action) => {
            const new_app_store_bot_list = action.payload;
            state.app_store_bot_list = [...new_app_store_bot_list];
            
            const new_bot_list = action.payload;
            // 使用new_bot_list 更新 state.bot_list，只是保留state.bot_list中bot的顺序
            // 1、删除废弃的bot
            const bot_list_1 = state.bot_list.filter((bot: Bot) => {
                for (let i = 0; i < new_bot_list.length; i++) {
                    if (bot.id === new_bot_list[i].id) {
                        return true;
                    }
                }
                return false;
                }
            );
            // 2、替换剩下的bot
            const bot_list_2 = bot_list_1.map((bot: Bot) => {
                const new_bot = new_bot_list.find((b: Bot) => b.id === bot.id);
                return new_bot;
            });
            // // 3、添加新增加的bot
            // new_bot_list.forEach((bot: Bot) => {
            //     if (!bot_list_2.find((b: Bot) => b.id === bot.id)) {
            //         bot_list_2.push(bot);
            //     }
            // });
            state.bot_list = [...bot_list_2];

            // 默认设置成为第1个
            if (!state.current_bot && state.bot_list && state.bot_list.length > 0) {
                state.current_bot = state.bot_list[0]
            } else {
                // 更新current_bot
                const new_current_bot = state.bot_list.find((bot: Bot) => bot.id === state.current_bot.id);
                if (new_current_bot) {
                    state.current_bot = new_current_bot;
                }
            }
        }
    },
})

// 生成redux store
const store = configureStore({
    reducer: {
        data: ReduxSlice.reducer,
    },
    middleware: [createLocalStorageMiddleware()]
});

const { open_bot, top_bot, delete_bot, update_bot_list, update_app_store_bot_list} = ReduxSlice.actions;

export {store, open_bot, top_bot, delete_bot, update_bot_list, update_app_store_bot_list}