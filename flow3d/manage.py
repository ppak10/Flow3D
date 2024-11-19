import argparse

from flow3d import Portfolio

# TODO: Find a better way to do this.
def parse_value(value):
    """
    Try to convert the value to the most appropriate type.
    Handles int, float, and string.
    """
    try:
        # Try converting to an integer
        return int(value)
    except ValueError:
        try:
            # Try converting to a float
            return float(value)
        except ValueError:
            # Return as string if neither int nor float
            return value

def main():
    parser = argparse.ArgumentParser(description="Manage and execute methods for `job`, `simulation`.")
    parser.add_argument(
        "method",
        help="Method within class (e.g., `create_job`).",
    )

    parser.add_argument(
        "--portfolio_path",
        default="/home/flow3d-docker/out",
        help="Defaults to `/home/flow3d-docker/out`.",
    )

    parser.add_argument("--verbose", help="Defaults to `False`.")

    args, unknown_args = parser.parse_known_args()

    portfolio = Portfolio(
        portfolio_path = args.portfolio_path,
        verbose = args.verbose,
    )

    # Separate positional and keyword arguments
    positional_args = []
    kwargs = {}

    for item in unknown_args:
        if "=" in item:
            try:
                key, value = item.split("=", 1)  # Split only at the first '='
                kwargs[key] = parse_value(value)
            except ValueError:
                print(f"Invalid format for keyword argument: {item}")
                return
        else:
            positional_args.append(parse_value(item))

    # Handle the commands
    try:
        method = getattr(portfolio, args.method)
        method(*positional_args, **kwargs)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
