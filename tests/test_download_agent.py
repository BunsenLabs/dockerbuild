from dockerbuild.download_agent import DownloadAgent

def test_canary_download(tmp_path, opts_nobody_uid_gid):
        gzip_header = bytes((0x1f, 0x8b))
        agent = DownloadAgent(opts_nobody_uid_gid)
        dest = tmp_path / "destination.tar.gz"
        result = agent.download("https://github.com/BunsenLabs/bunsen-os-release/archive/10.4.0-1.tar.gz", dest)
        assert result == True
        assert dest.is_file()
        assert dest.stat().st_size != 0
        assert dest.open("rb").read()[0:2] == gzip_header
