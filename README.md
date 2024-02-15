# youtube-chat

Do not forget to add real `.env` file if you need it.

jupyter lab --no-browser --ip 0.0.0.0 --port 4545 --allow-root --notebook-dir=.

docker build -t mind_arena .

docker run -it --init --volume="${PWD}:/app" mind_arena bash

docker run -d -it --init \
	--ipc=host \
	--volume="${PWD}:/app" \
	--publish="4545:4545" \
	--publish="7861:7861" \
	mind_arena bash

nohup python demo/main_multistage.py > demo.txt &

streamlit run main.py --server.address 0.0.0.0 --server.port 7860

make build

make run
