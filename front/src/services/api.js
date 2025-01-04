// src/services/api.js
import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000', // FastAPI base URL
    headers: {
        'Content-Type': 'application/json',
    }
});

export default {

    async getFile(ana_id, shapes_name) {
        try {
            const response = await apiClient.get(`/get_file/${ana_id}/${shapes_name}`);
            if (response.status == 200) {
                const resp = response.data
                return resp;
            } else {
                alert(response)
            }
        }
        catch (err) {
            throw new Error(err.message || 'Failed to fetch items');
        }
    },
    async saveShapes(ana_id, video_id, name, shapes) {
        try {
            const response = await apiClient.post('/save_shapes', { ana_id: ana_id, video_id: video_id, name: name, shapes: JSON.stringify(shapes) });
            if (response.status == 200) {
                const resp = response.data
                if (resp.code != '000') {
                    alert(resp.msg)
                    throw new Error(resp.msg)
                } else {
                    return resp;
                }

            } else {
                alert(response)
            }
        } catch (err) {
            throw new Error(err.message || 'Failed to fetch items');
        }
    },
    async getVideoInfo(ana_id, video_id) {
        try {
            const response = await apiClient.get(`/video_info/${ana_id}/${video_id}`);
            if (response.status == 200) {
                const resp = response.data
                if (resp.code != '000') {
                    alert(resp.msg)
                    throw new Error(resp.msg)
                } else {
                    return resp;
                }
            } else {
                alert(response)
            }
        }   catch (err) {
            throw new Error(err.message || 'Failed to getVideoInfo');
        }
    },
    async uploadVideo(ana_id, file) {
        try {
            console.log(123)
            //console.log(file.name)
            const formData = new FormData();
            formData.append('ana_id', ana_id);
            formData.append('file', file);
            formData.append('name', file.name);
            //formData.append('name', file.name);
            const response = await apiClient.post(`/upload_video`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            if (response.status == 200) {
                const resp = response.data
                if (resp.code != '000') {
                    alert(resp.msg)
                    throw new Error(resp.msg)
                } else {
                    return resp;
                }

            } else {
                alert(response)
            }
        } catch (err) {
            throw new Error(err.message || 'Failed to fetch items');
        }
    },
    async runOperation(ana_id, op, options) {
        try {
            const response = await apiClient.post('/run_operation', { ana_id: ana_id, op: op, options: options });
            if (response.status == 200) {
                const resp = response.data
                if (resp.code != '000') {
                    alert(resp.msg)
                    throw new Error(resp.msg)
                } else {
                    return resp;
                }

            } else {
                alert(response)
            }
        } catch (err) {
            throw new Error(err.message || 'Failed to fetch items');
        }
    },
    async createAnalysis(name) {
        try {
            const response = await apiClient.post('/create_analysis', { id: name, name: name });
            console.log(response)
            if (response.status == 200) {
                const resp = response.data
                if (resp.code != '000') {
                    alert(resp.msg)
                    throw new Error(resp.msg)
                } else {
                    return resp;
                }

            } else {
                alert(response.toString())
            }
        } catch (err) {
            throw new Error(err.message || 'Failed to fetch items');
        }
    },
    async getAnalysis() {
        try {
            const response = await apiClient.get('/list_analysis');
            if (response.status == 200) {
                const resp = response.data
                if (resp.code != '000') {
                    alert(resp.msg)
                    throw new Error(resp.msg)
                } else {
                    return resp;
                }

            } else {
                alert(response)
            }
        } catch (err) {
            throw new Error(err.message || 'Failed to fetch items');
        }
    },
    async getFiles(ana_id) {
        try {
            console.log(ana_id)
            const response = await apiClient.get('/list_files/' + ana_id);
            if (response.status == 200) {
                const resp = response.data
                if (resp.code != '000') {
                    alert(resp.msg)
                    throw new Error(resp.msg)
                } else {
                    return resp;
                }
            } else {
                alert(response)
            }
        } catch (err) {
            throw new Error(err.message || 'Failed to fetch items');
        }
    }

    // // GET request with query parameters
    // async getItems(queryParams = {}) {
    //     try {
    //         const response = await apiClient.get('/items', { params: queryParams });
    //         return response.data.items;
    //     } catch (err) {
    //         throw new Error(err.message || 'Failed to fetch items');
    //     }
    // },
    // // POST request with a JSON body
    // async createItem(itemData) {
    //     try {
    //         const response = await apiClient.post('/items', itemData);
    //         return response.data;
    //     } catch (err) {
    //         throw new Error(err.message || 'Failed to create item');
    //     }
    // },
    // // PUT request to update an item
    // async updateItem(itemId, itemData) {
    //     try {
    //         const response = await apiClient.put(`/items/${itemId}`, itemData);
    //         return response.data;
    //     } catch (err) {
    //         throw new Error(err.message || 'Failed to update item');
    //     }
    // },
    // // DELETE request to remove an item
    // async deleteItem(itemId) {
    //     try {
    //         const response = await apiClient.delete(`/items/${itemId}`);
    //         return response.data;
    //     } catch (err) {
    //         throw new Error(err.message || 'Failed to delete item');
    //     }
    // }
};