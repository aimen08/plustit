<template>
    <div>

        <div dir="auto" id="pell" class="pell" />

    </div>
</template>

<script>
import pell from 'pell'
import 'pell/dist/pell.css'
export default {
    methods: {
        ensureHTTP: str => /^https?:\/\//.test(str) && str || `http://${str}`
    },
    mounted() {
        pell.init({
            element: document.getElementById('pell'),
            onChange: html => {
                window.document.getElementById('pell-html-output').textContent = html
            },
            actions: [
                'bold',
                'italic',
                'underline',
                'strikethrough',
                'heading1',
                'heading2',
                'paragraph',
                'quote',
                'olist',
                'ulist',
                'code',
                'line',
                {
                    name: 'link',
                    result: () => {
                        const url = window.prompt('Enter the link URL')
                        if (url) pell.exec('createLink', this.ensureHTTP(url))
                    }
                }
            ]
        })
    }
}
</script>

<style>
.pell {
    margin-top: 20px;
    border: 1px solid gray;
    height: 300px;
    border-radius: 3px;
    direction: rtl;
    box-shadow: none;
}

#pell-html-output {
    margin: 0;
    white-space: pre-wrap;
}
</style>