import test

def test_f():
    t = test.Test()
    t.add_test_by_name('fake')
    t.run_test()


if __name__ == "__main__":
    test_f()
