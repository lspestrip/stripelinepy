subroutine test(a, b)
    real(kind=8), intent(in), dimension(:) :: a
    real(kind=8), intent(out), dimension(size(a)) :: b

    b = a
end subroutine test
