# https://www.notion.so/List-Of-Chains-2497cbaae9c6447b8bdb049e7acd806b
'''
Reece Williams | Notional - Started Oct 28th 2022

Requirements:
- must have ssh keys on github
- Have installed: git, gh, gofmt, golangci-lint

Goal:
- Auto git pull/clone latest repos we validate
- golang-cli lint / gofmt the files.\
    - let the user know this file needs work. Is there a way to auto gofmt/lint fix?
- Check files, see if it has dependabot. If not, add it in. [make this its own option, use pick]
- Add options for many different chains
- Get latest values in go.mod, toggle for state breaking or just minor version patches <- useful for security patches. Bump them

TODO: 
- when we update code, we need to create a new git branch for us to PR off of (do not build off of main) [probably fine with the vscode option]
- Multiple panels ex: repo management (download, pull/fetch, and sync branches)
'''

import os

from pick import pick
from CHAINS import VALIDATING_CHAINS
from Utils import *

# Panels
from Panel_Chains import ChainsPanel, Git
from Panel_Versions import VersionPanel
from Panel_Github import GithubPanel
from Panel_Lint import LintPanel
from Panel_Build import BuildPanel
from Panel_GoMod import GoModPanel

# === SETTINGS ===
SIMULATION = True

GO_MOD_REPLACES = {
    # make the right hand side the latest version from query 'panel -> v -> v   '
    "ibc": [
        ["github.com/cosmos/ibc-go/v5 v5.*.*", "github.com/cosmos/ibc-go/v5 v5.0.1"],
        ["github.com/cosmos/ibc-go/v4 v4.*.*", "github.com/cosmos/ibc-go/v4 v4.1.1"],
        ["github.com/cosmos/ibc-go/v3 v3.*.*", "github.com/cosmos/ibc-go/v3 v3.3.1"],
    ],
    "tendermint": [
        ["github.com/tendermint/tendermint v0.34.*", "github.com/tendermint/tendermint v0.34.22"],
        ["github.com/tendermint/tendermint v0.33.*", "github.com/tendermint/tendermint v0.33.9"],
        ["github.com/tendermint/tendermint v0.32.*", "github.com/tendermint/tendermint v0.33.14"],
    ],    
    "sdk": [
        ["github.com/cosmos/cosmos-sdk v0.46.*", "github.com/cosmos/cosmos-sdk v0.46.4"],
        ["github.com/cosmos/cosmos-sdk v0.45.*", "github.com/cosmos/cosmos-sdk v0.45.10"],
    ],    
    "wasmd": [
        ["github.com/CosmWasm/wasmd v0.29.*", "github.com/CosmWasm/wasmd v0.29.1"],        
    ],    
    "wasmvm": [
        ["github.com/CosmWasm/wasmvm v1.*.*", "github.com/CosmWasm/wasmvm v1.1.1 // indirect"],        
    ],
    "iavl": [
        ["github.com/cosmos/iavl v0.19.*", "github.com/cosmos/iavl v0.19.4 // indirect"],        
    ],
    # todo: way to add a replacement? ex: like was needed for dragonberry ics
}

MAJOR_REPOS = {
    "cosmos-sdk": "cosmos/cosmos-sdk",
    "ibc-go": "cosmos/ibc-go",
    "wasm": "CosmWasm/wasmd",
    "wasmvm": "CosmWasm/wasmvm",
    "tm": "tendermint/tendermint",
    "iavl": "cosmos/iavl",
}

# === FILE PATHS ===
current_dir = os.path.dirname(os.path.realpath(__file__))
yml_files = os.path.join(current_dir, ".yml_files")
test_output = os.path.join(current_dir, ".test_output")
WORKFLOWS = os.path.join(yml_files, "workflows")
ISSUE_TEMPLATE = os.path.join(yml_files, "TEMPLATES")

# === Create Dirs & Move to parent
os.chdir(current_dir)
for paths in [test_output, yml_files, WORKFLOWS, ISSUE_TEMPLATE]:    
    os.makedirs(paths, exist_ok=True)

# === Main ===
def main():    
    Chains().panel()

# === Panels ===
class Chains():
    def __init__(self) -> None:        
        if len(get_downloaded_chains()) == 0:
            chains = sorted([c[0] for c in get_chains()])
            select_download = [c[0] for c in pick(chains, "Select chains to download (none to download all)", min_selection_count=0, multiselect=True, indicator="=>")]
            if len(select_download) == 0:
                select_download = chains
            Git().download_chains_locally(select_download)

    def panel(self):
        options = {            
            "v": ["Version Panel", VersionPanel().panel, self.panel],
            "c": ["Chains Panel", ChainsPanel().panel, self.panel],   
            "g": ["Github Panel", GithubPanel().panel, self.panel],
            "l": ["Linting Panel", LintPanel().panel, self.panel],            
            "b": ["Build/Test Panel", BuildPanel().panel, self.panel],
            "m": ["GoMod Panel\n", GoModPanel().panel, self.panel],            

            "vsc": ["VSCode edit a chain", self.vscode_edit],

            "e": ["Exit", exit],
        }
        while True:
            selector("&c", "Chain Chores", options=options, aliases={})  

    def vscode_edit(self):
        chains = select_chains("Select chains to edit in VSCode", min_selection_count=1)
        for c in chains:
            os.system(f"code {os.path.join(current_dir, c)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("&cKeyboard Exit (^C)...")
